"""Author the requested notebook; all new analysis code is embedded in the notebook."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / 'notebooks/intel_pipeline_16_steps.ipynb'
if target.exists():
    raise FileExistsError(target)
cells = []
def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))
def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))

md('''
# Intel Image Classification — Pipeline 16 bước
**Practice 2 · PyTorch/torchvision · chạy local tại D:/Lab2**

Notebook có giải thích, code và kết quả thực. Chọn kernel **Lab2 (.venv)** và **Restart Kernel → Run All**.
Notebook dùng dataset, source và checkpoint trong project; không phải file độc lập với dữ liệu bên ngoài.

**Luồng:** Define Problem → EDA → Data Split → Cleaning → Feature Engineering → Baseline Model → Model Selection → Hyperparameter Tuning → Train Model → Evaluation Metrics → Cross Validation → Experiment Management → Statistical Validation → Error Analysis → Model Interpretability → Best Model.

**Ba loại bằng chứng:** (1) bảy run WF-002 đã huấn luyện, được xác minh và đọc lại;
(2) phân tích mới chạy trong notebook; (3) CV bổ sung cho linear probe trên DenseNet đóng băng.
Không diễn giải CV linear probe là CV của VGG11 fine-tune R07.

**Lưu ý thứ tự:** danh sách trên là bố cục trình bày. Khi làm thí nghiệm từ đầu, phải loại trùng/nhãn mâu thuẫn trước khi cố định split; CV để tuning phải nằm trước lần test cuối. Trong notebook này, test và lựa chọn cuối của WF-002 đã khóa; CV/thống kê được bổ sung hậu nghiệm và không chọn lại model.
''')
md('''
## 01. DEFINE PROBLEM — Xác định bài toán

Phân loại một ảnh phong cảnh vào một trong sáu lớp **buildings, forest, glacier, mountain, sea, street**.
Input: ảnh RGB. Output: sáu logits và nhãn argmax. Loss: CrossEntropyLoss.
Mục tiêu bài học: chuyển giao kiến thức ImageNet, thử kiến trúc/LR/batch, fine-tune và theo dõi TensorBoard.

Tiêu chí đã chốt: chọn checkpoint theo **validation accuracy cao nhất**, rồi validation loss thấp nhất,
epoch sớm nhất và run ID nhỏ nhất. Test accuracy và macro-F1 dùng báo cáo sau lựa chọn; đề không đặt ngưỡng accuracy bắt buộc.
''')
code(r'''
from pathlib import Path
import csv, gc, hashlib, html, inspect, json, math, os, sys, time
from collections import Counter
from statistics import NormalDist

ROOT = Path.cwd().resolve()
if ROOT.name == 'notebooks':
    ROOT = ROOT.parent
assert (ROOT / 'configs/experiments.json').exists(), 'Mở notebook từ D:/Lab2 hoặc D:/Lab2/notebooks'
sys.path.insert(0, str(ROOT)) if str(ROOT) not in sys.path else None
OUT = ROOT / 'outputs/pipeline_16_steps'
OUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(OUT / 'matplotlib-cache'))

import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader, TensorDataset
from torch.utils.tensorboard import SummaryWriter
from torchvision import transforms
from torchvision.models import DenseNet121_Weights
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, HTML, Image
from src.common import read_json, write_json, sha256, now
from src.phases.phase_02_data import RAW, CLASSES, MANIFEST
from src.phases.phase_03_models import build
from src.phases.phase_04_train import provenance, fingerprint, score
from src.phases.phase_05_evaluate import metrics

def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def table(rows):
    if not rows:
        print('Không có bản ghi.'); return
    columns = list(rows[0])
    esc = lambda x: html.escape(str(x))
    display(HTML('<table><thead><tr>' + ''.join('<th>'+esc(c)+'</th>' for c in columns) +
                 '</tr></thead><tbody>' + ''.join('<tr>'+''.join('<td>'+esc(r[c])+'</td>' for c in columns)+'</tr>' for r in rows)+'</tbody></table>'))

SEED = 42
DEVICE = 'xpu' if torch.xpu.is_available() else 'cpu'
torch.manual_seed(SEED)
np.random.seed(SEED)
manifest = read_csv(MANIFEST)
audit = read_json(ROOT / 'outputs/data/audit.json')
selection = read_json(ROOT / 'outputs/experiments/selection.json')
summary = read_json(ROOT / 'outputs/report/summary.json')
runs = [read_json(ROOT / f'outputs/experiments/R{i:02d}/result.json') for i in range(1, 8)]
assert sha256(MANIFEST) == audit['manifest_sha256']
assert selection['provenance_hash'] == fingerprint(provenance()), 'Artifact/source không khớp WF-002'
assert len(CLASSES) == 6 and all(r['status'] == 'COMPLETED' for r in runs)
print('Python:', sys.executable, '| device cho phân tích mới:', DEVICE)
table([{'label': i, 'class': name} for i, name in enumerate(CLASSES)])
''')
md('''
## 02. EDA — Khám phá dữ liệu

Chỉ khảo sát ảnh **training gốc** ở bước EDA để tránh dùng test định hướng thiết kế.
Khôi phục danh sách 14.034 ảnh training gốc từ train/validation manifest và audit các ảnh đã loại.
Đếm lớp, kích thước, chế độ màu và xem ví dụ. Ảnh trong `seg_pred` không có nhãn nên không dùng chấm điểm.
''')
code(r'''
development = [r for r in manifest if r['split'] != 'test']
original_train = development + audit['removed_train_duplicates']
assert len(original_train) == audit['original_train'] == 14034
original_counts = Counter(r['class_name'] for r in original_train)
sizes = np.array([[int(r['width']), int(r['height'])] for r in original_train])
table([{'class': c, 'original_train': original_counts[c]} for c in CLASSES])
print('Modes:', dict(Counter(r['original_mode'] for r in original_train)))
print('Min/median/max width:', sizes[:,0].min(), np.median(sizes[:,0]), sizes[:,0].max())
print('Min/median/max height:', sizes[:,1].min(), np.median(sizes[:,1]), sizes[:,1].max())
fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
axes[0].bar(CLASSES, [original_counts[c] for c in CLASSES], color='steelblue')
axes[0].set(title='Original training class counts', ylabel='Images')
axes[0].tick_params(axis='x', rotation=25)
axes[1].hist(sizes[:,0], bins=20, alpha=.65, label='width')
axes[1].hist(sizes[:,1], bins=20, alpha=.65, label='height')
axes[1].set(title='Original training image sizes', xlabel='Pixels', ylabel='Images')
axes[1].legend()
fig.savefig(OUT / 'eda.png', dpi=150); plt.show()

fig, axes = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
for ax, name in zip(axes.flat, CLASSES):
    row = next(r for r in original_train if r['class_name'] == name)
    with PILImage.open(RAW / row['relative_path']) as im:
        ax.imshow(im.convert('RGB'))
    ax.set_title(name); ax.axis('off')
plt.show()
''')
md('''
## 03. DATA SPLIT — Thiết kế và kiểm tra tập dữ liệu

Test giữ nguyên 3.000 ảnh từ nhà cung cấp. Phần train sau loại trùng được chia phân tầng khoảng 80/20,
seed 42; số validation mỗi lớp lấy floor(20%). Dataset/split là artifact đã thực hiện ở WF-002.
Ở bước này đọc và kiểm tra split hiện có; bước Cleaning bên dưới giải thích tiền điều kiện của split ấy.
Không tách lại sau khi đã xem test.
''')
code(r'''
split_rows = {s: [r for r in manifest if r['split'] == s] for s in ('train','validation','test')}
split_hashes = {s: {r['sha256'] for r in rows} for s, rows in split_rows.items()}
split_paths = {s: {r['relative_path'] for r in rows} for s, rows in split_rows.items()}
for a,b in [('train','validation'),('train','test'),('validation','test')]:
    assert not split_hashes[a] & split_hashes[b], (a,b,'hash leakage')
    assert not split_paths[a] & split_paths[b], (a,b,'path leakage')
table([{'class': c, **{s: sum(r['class_name']==c for r in rows) for s,rows in split_rows.items()}} for c in CLASSES])
print('Tổng:', {s: len(rows) for s,rows in split_rows.items()}, '| Không giao path/SHA256.')
assert [len(split_rows[s]) for s in ('train','validation','test')] == [11208,2798,3000]
''')
md('''
## 04. CLEANING — Làm sạch có kiểm chứng

WF-002 đã decode ảnh, kiểm tra kích thước và hash. Có **13 nhóm trùng byte nhưng khác nhãn**:
cách ly 23 ảnh training thuộc các nhóm đó; kết hợp trùng khác/chồng lấn test, loại tổng 28 bản ghi training.
**Giữ nguyên raw và test**, không tự đoán nhãn đúng. SHA256 chỉ phát hiện trùng byte, không nhận ra mọi ảnh gần giống.
Notebook kiểm lại tính toàn vẹn các ảnh giữ lại và thống kê lý do loại; không sửa ảnh gốc.
''')
code(r'''
conflicts = read_json(ROOT / 'outputs/data/label_conflicts.json')
removed = audit['removed_train_duplicates']
assert len(conflicts) == 13 and len(removed) == 28
table([{'reason': reason, 'count': count} for reason,count in Counter(r['reason'] for r in removed).items()])
assert len({r['sha256'] for r in development}) == len(development)
for i,row in enumerate(manifest, 1):
    if sha256(RAW / row['relative_path']) != row['sha256']:
        raise ValueError('Ảnh raw đã thay đổi: '+row['relative_path'])
print('Đã xác minh SHA256 của', len(manifest), 'ảnh giữ lại; raw không thay đổi.')
table([{'path':r['relative_path'], 'class':r['class_name'], 'reason':r['reason']} for r in removed[:8]])
''')
md('''
## 05. FEATURE ENGINEERING — Tiền xử lý và đặc trưng học sẵn

Với CNN, đặc trưng được học từ ảnh: không cần thủ công chuyển ảnh thành các cột màu/số cạnh.
RGB → resize cạnh ngắn 256 → crop 224 → tensor → chuẩn hóa mean/std ImageNet.
Train WF-002 dùng random crop/flip; validation/test dùng center crop.

CV bổ sung dùng **đặc trưng 1024 chiều của DenseNet121 ImageNet đóng băng**, center crop xác định và linear head mới.
Không fit scaler/PCA trên toàn bộ dữ liệu. Trích xuất chung được phép vì backbone chỉ có weights ImageNet,
không học từ nhãn của bất kỳ fold nào. Protocol này khác augmentation của R04–R06.
''')
code(r'''
MEAN = torch.tensor([.485,.456,.406]).view(3,1,1)
STD = torch.tensor([.229,.224,.225]).view(3,1,1)
eval_transform = DenseNet121_Weights.IMAGENET1K_V1.transforms()
train_transform = transforms.Compose([transforms.Resize(256),transforms.RandomCrop(224),
    transforms.RandomHorizontalFlip(),transforms.ToTensor(),transforms.Normalize(MEAN.flatten().tolist(),STD.flatten().tolist())])
example = RAW / split_rows['train'][0]['relative_path']
with PILImage.open(example) as im:
    rgb = im.convert('RGB')
    views = [eval_transform(rgb),train_transform(rgb),train_transform(rgb)]
assert all(t.shape == (3,224,224) and torch.isfinite(t).all() for t in views)
fig,axes = plt.subplots(1,3,figsize=(10,3),constrained_layout=True)
for ax,t,title in zip(axes,views,['Center crop (evaluation)','Random augmentation 1','Random augmentation 2']):
    ax.imshow((t*STD+MEAN).clamp(0,1).permute(1,2,0)); ax.set_title(title); ax.axis('off')
plt.show()
''')
md('''
## 06. BASELINE MODEL — Mốc so sánh đơn giản

Baseline **majority class** luôn đoán lớp nhiều nhất trong train; không nhìn validation/test để chọn lớp.
So sánh với mốc đoán ngẫu nhiên đều 1/6 ≈ 16,67% (kỳ vọng lý thuyết).
Đây là sanity baseline; R01/R04 là các baseline pretrained để so sánh kiến trúc ở bước kế tiếp.
''')
code(r'''
train_counts = Counter(int(r['label']) for r in split_rows['train'])
majority_label = max(range(6),key=lambda i:(train_counts[i],-i))
y_val = np.array([int(r['label']) for r in split_rows['validation']])
baseline_cm = np.zeros((6,6),dtype=int)
np.add.at(baseline_cm,(y_val,np.full(len(y_val),majority_label)),1)
baseline = metrics(baseline_cm)
assert baseline['samples'] == len(y_val)
table([{'baseline':'Majority: '+CLASSES[majority_label], 'validation_accuracy':baseline['accuracy'], 'macro_f1':baseline['macro_f1']},
       {'baseline':'Uniform random (theoretical expectation)', 'validation_accuracy':1/6, 'macro_f1':'Không giả lập'}])
''')
md('''
## 07. MODEL SELECTION — Chọn tập ứng viên

Hai ứng viên đáp ứng đề: **VGG11** (conv/pooling nối tiếp, classifier lớn) và **DenseNet121** (dense blocks chia sẻ đặc trưng).
Đầu ra ImageNet được thay bằng linear 6 lớp. Transfer chỉ học linear cuối; fine-tune mở block cuối.
Ở bước này xác định ứng viên; lựa chọn cuối phụ thuộc kết quả validation của toàn ma trận ở bước 8–9.
''')
code(r'''
preflight = read_json(ROOT / 'outputs/models/preflight.json')
table([{'model':r['model'],'mode':r['mode'],'total_parameters':r['parameters_total'],
        'trainable_parameters':r['parameters_trainable']} for r in preflight['records'] if r['batch']==8])
table([{'run':r['id'],'model':r['spec']['model'],'baseline_val_accuracy':r['best']['val_accuracy']}
       for r in runs if r['id'] in ('R01','R04')])
print('Hàm tạo model đã dùng trong WF-002:')
print(inspect.getsource(build))
''')
md('''
## 08. HYPERPARAMETER TUNING — So sánh cấu hình

Mỗi kiến trúc thử (LR 0.001, batch 8), (LR 0.0003, batch 8), (LR 0.001, batch 16).
Adam, seed 42, 5 epoch/run; mỗi biến thể chỉ đổi một yếu tố so với baseline cùng kiến trúc.
Bảng dưới dùng **validation**, không dùng test. Sáu cấu hình đã được chạy thật trong WF-002.
''')
code(r'''
table([{'run':r['id'],'architecture':r['spec']['model'],'lr':r['spec']['lr'],'batch':r['spec']['batch'],
        'best_epoch':r['best']['epoch'],'val_accuracy':r['best']['val_accuracy'],'val_loss':r['best']['val_loss']}
       for r in runs[:6]])
transfer_winner = min(runs[:6],key=lambda r:score(r['best']))
assert transfer_winner['id'] == selection['best_transfer']
print('Thắng transfer bằng validation:',transfer_winner['id'],transfer_winner['spec'])
''')
md('''
## 09. TRAIN MODEL — Huấn luyện và fine-tune

WF-002 đã chạy 30 epoch transfer và 3 epoch fine-tune. R07 khởi tạo từ **best checkpoint của R02**,
Adam mới LR 1e-5, mở block convolution cuối của VGG11 và linear cuối. Giữ dropout/BatchNorm ở eval.
Loss/accuracy tính theo số mẫu, có batch cuối; lưu best/last, optimizer, RNG, source/data/dependency hashes.

Mặc định notebook xác minh và trình bày các run đã hoàn tất, không tốn thêm hai giờ huấn luyện.
`RUN_EXISTING_TRAIN_PIPELINE=True` gọi pipeline gốc: run hoàn tất được kiểm tra/dùng lại, run dở được resume.
Muốn thử cấu hình mới cần tạo thí nghiệm mới; không ghi đè các run cũ.
''')
code(r'''
from src.phases import phase_04_train
RUN_EXISTING_TRAIN_PIPELINE = False
print(inspect.getsource(phase_04_train.epoch))
if RUN_EXISTING_TRAIN_PIPELINE:
    phase_04_train.run()
for result in runs:
    folder = ROOT / 'outputs/experiments' / result['id']
    for name,checksum in result['checkpoint_hashes'].items():
        assert sha256(folder/name)==checksum,(result['id'],name)
    assert len(result['history'])==result['spec']['epochs']
assert sum(len(r['history']) for r in runs)==33
print('VERIFIED: 7 run / 33 epoch và checksum best.pt/last.pt.')
display(Image(filename=str(ROOT/'outputs/report/learning_curves.png')))
''')
md('''
## 10. EVALUATION METRICS — Đánh giá trên test giữ riêng

Accuracy = số đúng / số ảnh. Precision, recall và F1 tính cho từng lớp; macro-F1 trung bình sáu F1 với trọng số bằng nhau.
Confusion matrix: **hàng nhãn thật, cột dự đoán**. Zero division = 0.
Đọc các dự đoán đã lưu, tính lại metrics độc lập với con số báo cáo; không chạy lại inference để tuning.
''')
code(r'''
predictions = {}
test_results = {}
for run_id in selection['test_runs']:
    saved = read_json(ROOT/f'outputs/report/{run_id}_test.json')
    path = ROOT/f'outputs/report/{run_id}_predictions.csv'
    assert sha256(path)==saved['predictions_sha256']
    rows = sorted(read_csv(path),key=lambda r:r['relative_path'])
    truth = np.array([int(r['truth']) for r in rows])
    predicted = np.array([int(r['prediction']) for r in rows])
    cm = np.zeros((6,6),dtype=int); np.add.at(cm,(truth,predicted),1)
    values = metrics(cm)
    assert values['accuracy']==saved['accuracy'] and values['macro_f1']==saved['macro_f1']
    assert len(rows)==3000 and selection['selected_before_test'] <= saved['evaluated']
    predictions[run_id] = rows; test_results[run_id] = values
table([{'run':k,'accuracy':v['accuracy'],'macro_f1':v['macro_f1'],'samples':v['samples']} for k,v in test_results.items()])
table(test_results[selection['final_run']]['per_class'])
display(Image(filename=str(ROOT/f'outputs/report/{selection["final_run"]}_confusion_matrix.png')))
''')
md('''
## 11. CROSS VALIDATION — Kiểm tra bổ sung bằng 5 fold

**Protocol riêng:** DenseNet121 ImageNet đóng băng + linear head 1024→6, center crop, Adam lr0.001,
batch256, 5 epoch mỗi fold; mỗi fold khởi tạo head mới. Chia phân tầng train+validation đã làm sạch,
không dùng test. Mỗi ảnh có đúng một dự đoán out-of-fold (OOF); không early-stop hoặc chọn epoch theo fold giữ lại.

Đây là CV của **linear probe**, không phải CV cho model R07 hay đánh giá không thiên lệch của cả quá trình chọn kiến trúc/tuning.
Nếu muốn đánh giá cả quy trình lựa chọn, cần nested CV hoặc tập kiểm chứng mới trong một nghiên cứu riêng.
Mean ± SD giữa fold mô tả độ dao động, không phải confidence interval của mô hình cuối.
Lần đầu cần trích đặc trưng khoảng vài phút; các lần sau dùng cache có fingerprint/checksum.
''')
code(r'''
CV_PROTOCOL = {'name':'densenet121_frozen_center_crop_linear_probe_v1','folds':5,'epochs':5,
               'lr':.001,'batch':256,'seed':42,'feature_batch':16}
cv_rows = sorted(development,key=lambda r:r['relative_path'])
cv_y = np.array([int(r['label']) for r in cv_rows])
cv_id = fingerprint({'protocol':CV_PROTOCOL,'manifest':sha256(MANIFEST),
                     'weights':read_json(ROOT/'outputs/models/weights.json')['densenet121'],
                     'torch':torch.__version__})
fold_id = np.full(len(cv_rows),-1,dtype=int)
generator = np.random.default_rng(SEED)
for label in range(6):
    indices = np.flatnonzero(cv_y==label); generator.shuffle(indices)
    for f,group in enumerate(np.array_split(indices,5)):
        fold_id[group]=f
assert np.all(fold_id>=0)
assert not {r['sha256'] for r in cv_rows} & split_hashes['test']
for f in range(5):
    a={cv_rows[i]['sha256'] for i in np.flatnonzero(fold_id!=f)}
    b={cv_rows[i]['sha256'] for i in np.flatnonzero(fold_id==f)}
    assert not a & b
table([{'fold':f+1,'train':int((fold_id!=f).sum()),'held_out':int((fold_id==f).sum())} for f in range(5)])

class FeatureImages(Dataset):
    def __len__(self): return len(cv_rows)
    def __getitem__(self,index):
        with PILImage.open(RAW/cv_rows[index]['relative_path']) as im:
            return eval_transform(im.convert('RGB'))

feature_file = OUT/'densenet_features.pt'
feature_meta = OUT/'densenet_features.json'
if feature_file.exists() and feature_meta.exists():
    metadata = read_json(feature_meta)
    assert metadata['fingerprint']==cv_id and metadata['sha256']==sha256(feature_file),'Stale feature cache'
    features = torch.load(feature_file,map_location='cpu',weights_only=True)
else:
    backbone = build('densenet121','transfer',SEED)
    backbone.classifier = nn.Identity()
    backbone.requires_grad_(False).eval().to(DEVICE)
    collected = []
    with torch.no_grad():
        for step,images in enumerate(DataLoader(FeatureImages(),batch_size=16,shuffle=False,num_workers=0),1):
            collected.append(backbone(images.to(DEVICE)).cpu())
            if step%100==0: print('Feature extraction:',min(step*16,len(cv_rows)),'/',len(cv_rows),flush=True)
    features = torch.cat(collected)
    temporary = feature_file.with_suffix('.tmp'); torch.save(features,temporary); temporary.replace(feature_file)
    write_json(feature_meta,{'fingerprint':cv_id,'sha256':sha256(feature_file),'created':now()})
    del backbone,collected; gc.collect()
    if DEVICE=='xpu': torch.xpu.empty_cache()
assert features.shape==(len(cv_rows),1024) and torch.isfinite(features).all()
print('Frozen features:',tuple(features.shape),'| no test images')
''')
code(r'''
cv_cache = OUT/'cross_validation.json'
oof_path = OUT/'cv_oof.csv'
if cv_cache.exists():
    cv_result = read_json(cv_cache)
    assert cv_result['fingerprint']==cv_id and cv_result['oof_sha256']==sha256(oof_path),'Stale CV cache'
    oof_rows = read_csv(oof_path)
    assert [r['relative_path'] for r in oof_rows]==[r['relative_path'] for r in cv_rows]
    oof = np.array([int(r['prediction']) for r in oof_rows])
    assert np.array_equal([int(r['fold']) for r in oof_rows],fold_id+1)
else:
    oof = np.full(len(cv_y),-1,dtype=int)
    fold_results = []
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(2)  # Small linear heads avoid large CPU thread-pool overhead.
    try:
        for f in range(5):
            torch.manual_seed(SEED+f)
            train_indices=np.flatnonzero(fold_id!=f); held_indices=np.flatnonzero(fold_id==f)
            head=nn.Linear(1024,6)
            optimizer=torch.optim.Adam(head.parameters(),lr=.001)
            batches=DataLoader(TensorDataset(features[train_indices],torch.tensor(cv_y[train_indices])),
                               batch_size=256,shuffle=True,generator=torch.Generator().manual_seed(SEED+f))
            with SummaryWriter(str(OUT/f'tensorboard/cv_fold_{f+1}'),purge_step=0) as writer:
                for ep in range(1,6):
                    total_loss=0.; samples=0
                    head.train()
                    for x,y in batches:
                        optimizer.zero_grad(set_to_none=True)
                        loss=nn.functional.cross_entropy(head(x),y)
                        assert torch.isfinite(loss)
                        loss.backward(); optimizer.step()
                        total_loss+=loss.item()*len(y); samples+=len(y)
                    writer.add_scalar('train/loss',total_loss/samples,ep)
                head.eval()
                with torch.no_grad():
                    oof[held_indices]=head(features[held_indices]).argmax(1).numpy()
                cm=np.zeros((6,6),dtype=int); np.add.at(cm,(cv_y[held_indices],oof[held_indices]),1)
                result=metrics(cm)
                row={'fold':f+1,'samples':len(held_indices),'accuracy':result['accuracy'],'macro_f1':result['macro_f1']}
                fold_results.append(row)
                writer.add_scalar('held_out/accuracy',row['accuracy'],5)
                writer.add_scalar('held_out/macro_f1',row['macro_f1'],5)
                print('CV:',row,flush=True)
            del head,optimizer,batches
    finally:
        torch.set_num_threads(previous_threads)
    with oof_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['relative_path','fold','truth','prediction']); w.writeheader()
        w.writerows({'relative_path':r['relative_path'],'fold':int(fold_id[i]+1),'truth':int(cv_y[i]),'prediction':int(oof[i])}
                    for i,r in enumerate(cv_rows))
    cv_result={'status':'COMPLETED','fingerprint':cv_id,'protocol':CV_PROTOCOL,'created':now(),
               'fold_results':fold_results,'oof_sha256':sha256(oof_path)}
    write_json(cv_cache,cv_result)
assert oof.shape==cv_y.shape and np.all((oof>=0)&(oof<6))
assert len(read_csv(oof_path))==len(cv_rows)==14006
for row in cv_result['fold_results']:
    mask=fold_id==row['fold']-1
    assert np.isclose((oof[mask]==cv_y[mask]).mean(),row['accuracy'])
cv_scores=np.array([r['accuracy'] for r in cv_result['fold_results']])
table(cv_result['fold_results'])
print(f'Linear-probe CV accuracy: mean={cv_scores.mean():.2%}, sample SD={cv_scores.std(ddof=1):.2%}')
print('Đây KHÔNG phải CV accuracy của R07.')
''')
md('''
## 12. EXPERIMENT MANAGEMENT — Quản lý và truy vết

WF-002: config, source/data/dependency hashes, best/last checkpoints, RNG, lịch sử và TensorBoard riêng từng run.
Notebook bổ sung: cache feature/CV riêng trong `outputs/pipeline_16_steps`, không ghi đè run R01–R07.
Mở cả log cũ và CV: `python -m tensorboard.main --logdir D:/Lab2/outputs --host 127.0.0.1 --port 6007`.
Nếu server cũ ở port6006 còn chạy, nó chỉ theo dõi `outputs/experiments`.
''')
code(r'''
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
tracking=[]
for r in runs:
    directory=ROOT/'outputs/experiments'/r['id']
    identity=read_json(directory/'identity.json')
    assert fingerprint({k:v for k,v in identity.items() if k!='fingerprint'})==r['fingerprint']
    events=EventAccumulator(str(directory/'tensorboard')).Reload()
    for tag in ['train/loss','train/accuracy','validation/loss','validation/accuracy']:
        assert len(events.Scalars(tag))==r['spec']['epochs']
    tracking.append({'run':r['id'],'fingerprint':r['fingerprint'][:16], 'epochs':r['spec']['epochs'],
                     'device':r['device'],'minutes_train_validation':round(r['seconds']/60,2)})
table(tracking)
write_json(OUT/'analysis_manifest.json',{'created':now(),'original_selection_sha256':sha256(ROOT/'outputs/experiments/selection.json'),
          'data_manifest_sha256':sha256(MANIFEST),'cv_fingerprint':cv_id,'seed':SEED,'device_for_new_analysis':DEVICE,
          'original_runs':[r['fingerprint'] for r in runs]})
''')
md('''
## 13. STATISTICAL VALIDATION — Khoảng tin cậy và so sánh theo cặp

Tính **Wilson 95% CI** cho test accuracy R07; **paired bootstrap** 2.000 lần cho chênh lệch accuracy R07−R02;
**McNemar exact hai phía** cho hai mô hình dự đoán cùng các ảnh. So sánh này giữ nguyên cặp ảnh, không bootstrap hai model độc lập.

Phân tích hậu nghiệm của một cặp đã xác định, không dùng p-value để đổi model. Khoảng tin cậy giả định các ảnh độc lập;
ảnh gần giống và sự phụ thuộc trong dataset có thể làm khoảng quá hẹp. Bootstrap ảnh không đo biến thiên do seed huấn luyện.
P-value không phải xác suất mô hình đúng và không thay thế đánh giá mức chênh lệch thực tế.

Tham khảo phép kiểm định nhị thức chính xác: [SciPy binomtest](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html).
Code dưới dùng thư viện chuẩn và NumPy, không cần cài SciPy.
''')
code(r'''
def wilson(success,n,confidence=.95):
    assert 0<=success<=n and n>0
    z=NormalDist().inv_cdf((1+confidence)/2); p=success/n; den=1+z*z/n
    center=(p+z*z/(2*n))/den
    radius=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0.,center-radius),min(1.,center+radius)

def mcnemar_exact(b,c):
    n=int(b+c)
    if n==0: return 1.
    return min(1.,2*sum(math.comb(n,k) for k in range(min(int(b),int(c))+1))/(2**n))

assert abs(mcnemar_exact(10,0)-.001953125)<1e-12
assert mcnemar_exact(0,0)==1 and mcnemar_exact(5,5)==1
assert np.isclose(wilson(0,10)[0],0) and np.isclose(wilson(10,10)[1],1)
a=predictions['R02']; b=predictions['R07']
assert [r['relative_path'] for r in a]==[r['relative_path'] for r in b]
assert [r['truth'] for r in a]==[r['truth'] for r in b]
correct_a=np.array([r['truth']==r['prediction'] for r in a])
correct_b=np.array([r['truth']==r['prediction'] for r in b])
delta=correct_b.astype(float)-correct_a.astype(float)
rng=np.random.default_rng(SEED)
bootstrap=np.concatenate([delta[rng.integers(0,len(delta),size=(100,len(delta)))].mean(axis=1) for _ in range(20)])
bootstrap_ci=np.quantile(bootstrap,[.025,.975])
old_only=int((correct_a & ~correct_b).sum()); new_only=int((~correct_a & correct_b).sum())
statistical={'comparison':'R07 minus R02 (post-hoc paired analysis)', 'n':len(delta),
 'accuracy_R07':float(correct_b.mean()),'wilson_95_accuracy_R07':list(wilson(int(correct_b.sum()),len(delta))),
 'accuracy_difference':float(delta.mean()),'paired_bootstrap_95_difference':bootstrap_ci.tolist(),
 'bootstrap_replicates':2000,'R02_only_correct':old_only,'R07_only_correct':new_only,
 'mcnemar_exact_two_sided_p':mcnemar_exact(old_only,new_only),'seed':SEED}
write_json(OUT/'statistical_validation.json',statistical)
table([{'quantity':k,'value':v} for k,v in statistical.items()])
print(f'Delta={delta.mean()*100:+.2f} điểm %, bootstrap95%=[{bootstrap_ci[0]*100:.2f}, {bootstrap_ci[1]*100:.2f}] điểm %.')
print('Suy luận chỉ áp dụng theo giả định độc lập và phạm vi so sánh hậu nghiệm đã nêu.')
''')
md('''
## 14. ERROR ANALYSIS — Phân tích lỗi

Xếp các cặp nhầm lẫn theo số ảnh và xem ví dụ sai thật. Những ví dụ này chỉ để hiểu lỗi sau đánh giá;
không dùng sửa nhãn, điều chỉnh model hoặc tái chọn checkpoint trong bài đã hoàn tất.
Ví dụ được chọn theo thứ tự đường dẫn, không đại diện thống kê cho mọi lỗi.
''')
code(r'''
final_id=selection['final_run']
final_predictions=predictions[final_id]
cm=np.array(test_results[final_id]['confusion_matrix'])
pairs=sorted([{'true':CLASSES[i],'predicted':CLASSES[j],'count':int(cm[i,j])}
              for i in range(6) for j in range(6) if i!=j],key=lambda r:-r['count'])
table(pairs[:8])
errors=[r for r in final_predictions if r['truth']!=r['prediction']]
assert len(errors)==int(cm.sum()-cm.trace())
print('Số lỗi:',len(errors),'/',int(cm.sum()))
fig,axes=plt.subplots(3,3,figsize=(10,10),constrained_layout=True)
for ax,row in zip(axes.flat,errors[:9]):
    with PILImage.open(RAW/row['relative_path']) as im: ax.imshow(im.convert('RGB'))
    ax.set_title('True: '+CLASSES[int(row['truth'])]+'\nPred: '+CLASSES[int(row['prediction'])],fontsize=10)
    ax.axis('off')
fig.savefig(OUT/'error_examples.png',dpi=140); plt.show()
''')
md('''
## 15. MODEL INTERPRETABILITY — Grad-CAM

Grad-CAM dùng gradient của logit lớp dự đoán theo activation ở convolution cuối, lấy trung bình gradient theo không gian
làm trọng số rồi cộng các feature maps và ReLU. Heatmap được nội suy lên crop224×224 đã đưa vào model.
Đây là vùng liên quan đến điểm dự đoán trong phép xấp xỉ này, **không chứng minh quan hệ nhân quả hoặc model hiểu đúng cảnh**.

Xem một ảnh đoán đúng và một ảnh đoán sai, chọn xác định theo đường dẫn. Chuẩn hóa heatmap riêng mỗi ảnh,
nên không so sánh cường độ tuyệt đối giữa hai ảnh.
Nguồn: [bài báo Grad-CAM](https://arxiv.org/abs/1610.02391), [Captum LayerGradCam](https://captum.ai/api/layer.html).
''')
code(r'''
final_run=next(r for r in runs if r['id']==final_id)
best_path=ROOT/'outputs/experiments'/final_id/'best.pt'
assert sha256(best_path)==final_run['checkpoint_hashes']['best.pt']
model=build(final_run['spec']['model'],final_run['spec']['mode'],SEED)
checkpoint=torch.load(best_path,map_location='cpu',weights_only=False)  # Only this verified project-created checkpoint.
model.load_state_dict(checkpoint['model']); del checkpoint
model.requires_grad_(False).eval().to(DEVICE)
assert final_run['spec']['model']=='vgg11','Grad-CAM layer mapping here is for the selected VGG11.'
layer=model.features[18]

def gradcam(row):
    with PILImage.open(RAW/row['relative_path']) as im: x=eval_transform(im.convert('RGB')).unsqueeze(0)
    x=x.to(DEVICE).requires_grad_(True)
    activation=[]
    def capture(module,inputs,output):
        activation.append(output)
        output.retain_grad()
    handle=layer.register_forward_hook(capture)
    try:
        logits=model(x); predicted=int(logits.argmax(1).item())
        model.zero_grad(set_to_none=True)
        logits[0,predicted].backward()
        a=activation[0]
        assert a.grad is not None and torch.isfinite(a.grad).all()
        weights=a.grad.mean(dim=(2,3),keepdim=True)
        heat=torch.relu((weights*a).sum(dim=1,keepdim=True))
        heat=nn.functional.interpolate(heat,size=(224,224),mode='bilinear',align_corners=False)[0,0]
        peak=float(heat.max().item())
        heat=(heat/peak if peak>0 else torch.zeros_like(heat)).detach().cpu().numpy()
        view=(x[0].detach().cpu()*STD+MEAN).clamp(0,1).permute(1,2,0).numpy()
        assert heat.shape==(224,224) and np.isfinite(heat).all()
        return view,heat,predicted,peak
    finally:
        handle.remove()

correct_example=next(r for r in final_predictions if r['truth']==r['prediction'])
cam_examples=[correct_example,errors[0]]
fig,axes=plt.subplots(2,3,figsize=(11,7),constrained_layout=True)
cam_metadata=[]
for axes_row,row in zip(axes,cam_examples):
    view,heat,predicted,peak=gradcam(row)
    assert predicted==int(row['prediction']),'Prediction differs from saved checkpoint evaluation'
    axes_row[0].imshow(view); axes_row[0].set_title('True: '+CLASSES[int(row['truth'])])
    axes_row[1].imshow(heat,cmap='inferno',vmin=0,vmax=1); axes_row[1].set_title('Grad-CAM (relative)')
    axes_row[2].imshow(view); axes_row[2].imshow(heat,cmap='inferno',alpha=.45,vmin=0,vmax=1)
    axes_row[2].set_title('Pred: '+CLASSES[predicted])
    for ax in axes_row: ax.axis('off')
    cam_metadata.append({'path':row['relative_path'],'prediction':predicted,'heatmap_peak_before_normalization':peak})
fig.savefig(OUT/'gradcam.png',dpi=150); plt.show()
write_json(OUT/'gradcam_examples.json',cam_metadata)
''')
md('''
## 16. BEST MODEL — Mô hình bàn giao

Model cuối giữ nguyên quyết định WF-002 trước test. CV, p-value và Grad-CAM trong notebook này không thay đổi quyết định ấy.
Checkpoint là `best.pt`, không mặc định là epoch cuối. Hàm dưới dùng model đã nạp để dự đoán ảnh mới;
softmax nếu dùng chỉ là điểm số mô hình, chưa được hiệu chỉnh xác suất.
''')
code(r'''
assert final_id==min(runs,key=lambda r:score(r['best']))['id']
final_metrics=test_results[final_id]
table([{'run':final_id,'architecture':final_run['spec']['model'],'mode':final_run['spec']['mode'],
        'validation_accuracy':final_run['best']['val_accuracy'],'test_accuracy':final_metrics['accuracy'],
        'test_macro_f1':final_metrics['macro_f1'],'checkpoint':str(best_path)}])

def predict_image(path):
    with PILImage.open(path) as im: x=eval_transform(im.convert('RGB')).unsqueeze(0).to(DEVICE)
    with torch.no_grad(): label=int(model(x).argmax(1).item())
    return {'label':label,'class_name':CLASSES[label]}

print('Ví dụ inference:',predict_image(RAW/correct_example['relative_path']))
write_json(OUT/'notebook_validation.json',{'status':'PASSED','finished':now(),'sections':16,'original_runs':7,
 'original_epochs':33,'test_samples':3000,'cv_folds':5,'cv_oof_samples':len(oof),
 'cv_protocol':CV_PROTOCOL['name'],'gradcam_examples':len(cam_examples),'final_run':final_id,
 'note':'CV is a separate frozen DenseNet linear probe, not cross-validation of R07.'})
print('PASS: leakage, hashes, checkpoint, metric, OOF, statistical self-checks, TensorBoard và Grad-CAM.')
del model; gc.collect()
if DEVICE=='xpu': torch.xpu.empty_cache()
''')
md('''
**Kết luận:** trình bày đủ 16 bước; bảy run gốc có bằng chứng, CV linear-probe có OOF riêng,
thống kê và giải thích được gắn với các giới hạn phù hợp. Một seed và một dataset chưa chứng minh hiệu năng ngoài dữ liệu này.
Xem thêm `../outputs/report/report.md` và `../docs/nhan_xet_ket_qua.md` trong project.
''')
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Lab2 (.venv)','language':'python','name':'lab2'},
                                         'language_info':{'name':'python'}})
nbf.validate(nb)
target.parent.mkdir(exist_ok=True)
nbf.write(nb,target)
print('Created',target,'with',len(cells),'cells')

if __name__=='__main__':
    headings=[c.source for c in cells if c.cell_type=='markdown' and c.source.startswith('## ')]
    assert len(headings)==16
    for cell in cells:
        if cell.cell_type=='code': compile(cell.source,str(target),'exec')
    print('16 sections and all code cells compile.')
