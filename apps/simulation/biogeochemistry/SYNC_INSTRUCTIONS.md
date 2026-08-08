# همسان‌سازی (Sync) با پروژه محلی

## روش پیشنهادی (rsync یا git)

### ۱. اگر مخزن git دارید:
```bash
# از ریشه پروژه محلی
git remote add origin <URL-مخزن>
git fetch origin
git checkout -b feature/daycent-seven-pool
# کپی فایل‌های تولید شده
cp -r /path/to/artifacts/apps ./
git add apps/satellite/algorithms/sebs.py \
        apps/satellite/algorithms/kriging.py \
        apps/simulation/biogeochemistry/daycent_seven_pool.py
git commit -m "Sprint 0: SEBS + Kriging precip + DayCent 7-pool"
git push -u origin feature/daycent-seven-pool
```

### ۲. همسان‌سازی مستقیم با rsync (بدون git):
```bash
# از ماشین دارای artifacts
rsync -av --progress \
  /home/workdir/artifacts/apps/ \
  user@local-machine:/path/to/your/project/apps/
```

### ۳. دستور یک‌خطی برای کپی داخل همان میزبان:
```bash
PROJECT_ROOT=/path/to/your/local/project
mkdir -p $PROJECT_ROOT/apps/satellite/algorithms
mkdir -p $PROJECT_ROOT/apps/simulation/biogeochemistry
cp apps/satellite/algorithms/sebs.py          $PROJECT_ROOT/apps/satellite/algorithms/
cp apps/satellite/algorithms/kriging.py       $PROJECT_ROOT/apps/satellite/algorithms/
cp apps/simulation/biogeochemistry/daycent_seven_pool.py \
                                               $PROJECT_ROOT/apps/simulation/biogeochemistry/
```

### وابستگی‌ها
```bash
pip install numpy scipy
```

پس از کپی، تست‌ها:
```bash
python -m apps.satellite.algorithms.sebs
python -m apps.satellite.algorithms.kriging
python -m apps.simulation.biogeochemistry.daycent_seven_pool
```
