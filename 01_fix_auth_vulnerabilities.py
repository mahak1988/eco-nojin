#!/usr/bin/env python3
"""
اصلاح ۱: رفع باگ امنیتی زنده در endpointهای شبیه‌سازی
=========================================================
مشکلات رفع‌شده (طبق بررسی فنی قبلی):

1. POST /scenarios (apps/simulation/scenario/router.py):
   - هیچ Depends احراز هویتی نداشت.
   - user_id با uuid.uuid4() تصادفی ساخته می‌شد (هرگز به کاربر واقعی متصل نمی‌شد).

2. POST/GET /simulation/runs (apps/simulation/runs/router.py):
   - user_id مستقیماً از بدنهٔ درخواست/کوئری کلاینت خوانده می‌شد (بدون auth) —
     یعنی هر کاربر می‌توانست به‌جای هر user_id دلخواه، رکورد بسازد یا رکورد
     کاربر دیگر را با حدس user_id فهرست کند (IDOR).

3. ناسازگاری نوع ستون user_id:
   - apps/users/models.py: User.id عدد صحیح (Integer) است.
   - apps/simulation/scenario/models.py: user_id از نوع UUID تعریف شده بود.
   - apps/simulation/runs/models.py: user_id از نوع String(36) تعریف شده بود.
   این یعنی حتی با auth واقعی، current_user.id (int) در ستون UUID/String قابل
   ذخیرهٔ صحیح نبود. این اسکریپت نوع ستون‌ها را به Integer + ForeignKey به
   users.id اصلاح می‌کند و یک migration آلمبیک جدید اضافه می‌کند.

پس از اجرا حتماً `alembic upgrade head` را روی دیتابیس اجرا کنید.
"""
from __future__ import annotations

from _common import get_repo_root, replace_once, read, write, section

REPO = get_repo_root()


def fix_scenario_router() -> None:
    section("۱.۱ افزودن auth واقعی به apps/simulation/scenario/router.py")
    path = REPO / "apps/simulation/scenario/router.py"

    replace_once(
        path,
        old='from apps.shared_core.database.session import get_db_session\n'
            'from apps.simulation.scenario.models import (',
        new='from apps.shared_core.database.session import get_db_session\n'
            'from apps.users.dependencies import get_current_user\n'
            'from apps.users.models import User\n'
            'from apps.simulation.scenario.models import (',
        label="import get_current_user و User",
    )

    replace_once(
        path,
        old='@router.post("/scenarios", response_model=ScenarioResponse, status_code=201)\n'
            'async def create_scenario(\n'
            '    data: ScenarioCreate,\n'
            '    db: AsyncSession = Depends(get_db_session),\n'
            '):',
        new='@router.post("/scenarios", response_model=ScenarioResponse, status_code=201)\n'
            'async def create_scenario(\n'
            '    data: ScenarioCreate,\n'
            '    db: AsyncSession = Depends(get_db_session),\n'
            '    current_user: User = Depends(get_current_user),\n'
            '):',
        label="افزودن Depends(get_current_user) به create_scenario",
    )

    replace_once(
        path,
        old='    scenario = Scenario(\n'
            '        id=uuid.uuid4(),\n'
            '        user_id=uuid.uuid4(),  # TODO: از auth واقعی استفاده شود\n',
        new='    scenario = Scenario(\n'
            '        id=uuid.uuid4(),\n'
            '        user_id=current_user.id,\n',
        label="استفاده از current_user.id به‌جای uuid تصادفی",
    )


def fix_scenario_models() -> None:
    section("۱.۲ اصلاح نوع ستون user_id در apps/simulation/scenario/models.py")
    path = REPO / "apps/simulation/scenario/models.py"
    content = read(path)

    if "ForeignKey" not in content:
        content = content.replace(
            "from sqlalchemy import",
            "from sqlalchemy import ForeignKey,",
            1,
        )

    old_uuid_col = 'user_id = Column(UUID(as_uuid=True), nullable=False, index=True)'
    new_int_col = (
        'user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), '
        'nullable=False, index=True)'
    )
    count = content.count(old_uuid_col)
    if count == 0 and new_int_col in content:
        print("  [skip] user_id ستون‌ها: به‌نظر قبلاً اعمال شده")
    elif count == 0:
        print("  [WARN] الگوی user_id UUID پیدا نشد — دستی بررسی کنید")
    else:
        content = content.replace(old_uuid_col, new_int_col)
        if "Integer" not in content.split("from sqlalchemy import", 1)[1].split("\n", 1)[0]:
            content = content.replace(
                "from sqlalchemy import ForeignKey,",
                "from sqlalchemy import ForeignKey, Integer,",
                1,
            )
        write(path, content)
        print(f"  [ok] {count} ستون user_id از UUID به Integer+ForeignKey اصلاح شد")


def fix_runs_router_and_model() -> None:
    section("۱.۳ رفع IDOR در apps/simulation/runs/router.py + نوع ستون")
    router_path = REPO / "apps/simulation/runs/router.py"
    model_path = REPO / "apps/simulation/runs/models.py"

    replace_once(
        router_path,
        old="from apps.shared_core.database.session import get_db_session\n"
            "from apps.simulation.runs.models import SimulationRun",
        new="from apps.shared_core.database.session import get_db_session\n"
            "from apps.users.dependencies import get_current_user\n"
            "from apps.users.models import User\n"
            "from apps.simulation.runs.models import SimulationRun",
        label="import get_current_user و User در runs/router.py",
    )

    replace_once(
        router_path,
        old="class RunCreate(BaseModel):\n"
            "    simulator_id: str\n"
            "    simulator_name: str = \"\"\n"
            "    parameters: dict = Field(default_factory=dict)\n"
            "    metrics: dict = Field(default_factory=dict)\n"
            "    advisory: dict = Field(default_factory=dict)\n"
            "    scenario_name: Optional[str] = None\n"
            "    note: Optional[str] = Field(default=None, max_length=1000)\n"
            "    user_id: Optional[str] = None\n",
        new="class RunCreate(BaseModel):\n"
            "    simulator_id: str\n"
            "    simulator_name: str = \"\"\n"
            "    parameters: dict = Field(default_factory=dict)\n"
            "    metrics: dict = Field(default_factory=dict)\n"
            "    advisory: dict = Field(default_factory=dict)\n"
            "    scenario_name: Optional[str] = None\n"
            "    note: Optional[str] = Field(default=None, max_length=1000)\n"
            "    # user_id دیگر از کلاینت گرفته نمی‌شود؛ از current_user احراز-هویت‌شده می‌آید\n",
        label="حذف user_id قابل‌جعل از RunCreate",
    )

    replace_once(
        router_path,
        old='@router.post("", summary="Save a simulation run to the dashboard")\n'
            'async def save_run(data: RunCreate, db: AsyncSession = Depends(get_db_session)) -> None:\n'
            '    """Handle save_run (data, db)."""\n'
            '    await _ensure_table(db)\n'
            '    run = SimulationRun(\n'
            '        id=str(uuid.uuid4()),\n'
            '        user_id=data.user_id,\n',
        new='@router.post("", summary="Save a simulation run to the dashboard")\n'
            'async def save_run(\n'
            '    data: RunCreate,\n'
            '    db: AsyncSession = Depends(get_db_session),\n'
            '    current_user: User = Depends(get_current_user),\n'
            ') -> None:\n'
            '    """Handle save_run (data, db)."""\n'
            '    await _ensure_table(db)\n'
            '    run = SimulationRun(\n'
            '        id=str(uuid.uuid4()),\n'
            '        user_id=current_user.id,\n',
        label="save_run: احراز هویت الزامی + user_id از توکن",
    )

    replace_once(
        router_path,
        old='@router.get("", summary="List saved runs (newest first)")\n'
            'async def list_runs(\n'
            '    simulator_id: Optional[str] = Query(None),\n'
            '    user_id: Optional[str] = Query(None),\n'
            '    limit: int = Query(50, ge=1, le=200),\n'
            '    db: AsyncSession = Depends(get_db_session),\n'
            '):\n'
            '    """Handle list_runs (simulator_id, user_id, limit, db)."""\n'
            '    q = select(SimulationRun).order_by(desc(SimulationRun.created_at)).limit(limit)\n'
            '    if simulator_id:\n'
            '        q = q.where(SimulationRun.simulator_id == simulator_id)\n'
            '    if user_id:\n'
            '        q = q.where(SimulationRun.user_id == user_id)\n',
        new='@router.get("", summary="List saved runs (newest first)")\n'
            'async def list_runs(\n'
            '    simulator_id: Optional[str] = Query(None),\n'
            '    limit: int = Query(50, ge=1, le=200),\n'
            '    db: AsyncSession = Depends(get_db_session),\n'
            '    current_user: User = Depends(get_current_user),\n'
            '):\n'
            '    """Handle list_runs (simulator_id, limit, db)."""\n'
            '    # فقط رکوردهای خودِ کاربر لاگین‌شده برمی‌گردد (قبلاً هر user_id دلخواه قابل جست‌وجو بود)\n'
            '    q = (\n'
            '        select(SimulationRun)\n'
            '        .where(SimulationRun.user_id == current_user.id)\n'
            '        .order_by(desc(SimulationRun.created_at))\n'
            '        .limit(limit)\n'
            '    )\n'
            '    if simulator_id:\n'
            '        q = q.where(SimulationRun.simulator_id == simulator_id)\n',
        label="list_runs: فقط رکوردهای همان کاربر، بدون امکان جعل user_id",
    )

    # نوع ستون user_id در مدل
    content = read(model_path)
    old = 'user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)'
    new = (
        'user_id: Mapped[Optional[int]] = mapped_column(\n'
        '        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True\n'
        '    )'
    )
    if old in content:
        content = content.replace(old, new)
        if "ForeignKey" not in content.split("from sqlalchemy import", 1)[1].split("\n", 1)[0]:
            content = content.replace(
                "from sqlalchemy import String, Text, DateTime, JSON",
                "from sqlalchemy import String, Text, DateTime, JSON, Integer, ForeignKey",
                1,
            )
        write(model_path, content)
        print("  [ok] SimulationRun.user_id از String(36) به Integer+ForeignKey اصلاح شد")
    elif "ForeignKey" in content and "user_id: Mapped[Optional[int]]" in content:
        print("  [skip] SimulationRun.user_id: به‌نظر قبلاً اعمال شده")
    else:
        print("  [WARN] الگوی user_id در runs/models.py پیدا نشد — دستی بررسی کنید")


MIGRATION_TEMPLATE = '''"""Fix user_id column types to Integer FK -> users.id

Revision ID: 0003_fix_user_id_types
Revises: 0002_core_models
Create Date: {date}

قبل از این migration، ستون user_id در جدول‌های scenarios، scenario_results،
comparison_sessions از نوع UUID و در simulation_runs از نوع String(36) بود؛
این نوع‌ها با apps.users.models.User.id (Integer) ناسازگار بودند و مانع
اتصال صحیح این رکوردها به کاربر واقعی می‌شدند.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_fix_user_id_types"
down_revision = "0002_core_models"
branch_labels = None
depends_on = None


TABLES_UUID_TO_INT = ["scenarios", "scenario_results", "comparison_sessions"]


def upgrade() -> None:
    for table in TABLES_UUID_TO_INT:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(
                "user_id",
                type_=sa.Integer(),
                postgresql_using="NULL",  # داده‌ی UUID قدیمی قابل نگاشت مستقیم به Integer نیست
                existing_nullable=False,
            )
            batch_op.create_foreign_key(
                f"fk_{{table}}_user_id_users",
                "users",
                ["user_id"],
                ["id"],
                ondelete="CASCADE",
            )

    with op.batch_alter_table("simulation_runs") as batch_op:
        batch_op.alter_column(
            "user_id",
            type_=sa.Integer(),
            postgresql_using="NULL",
            existing_nullable=True,
        )
        batch_op.create_foreign_key(
            "fk_simulation_runs_user_id_users",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    for table in TABLES_UUID_TO_INT:
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_constraint(f"fk_{{table}}_user_id_users", type_="foreignkey")
            batch_op.alter_column("user_id", type_=sa.String(36))

    with op.batch_alter_table("simulation_runs") as batch_op:
        batch_op.drop_constraint("fk_simulation_runs_user_id_users", type_="foreignkey")
        batch_op.alter_column("user_id", type_=sa.String(36))
'''


def add_migration() -> None:
    section("۱.۴ افزودن Alembic migration برای تغییر نوع ستون‌ها")
    import datetime

    out_path = REPO / "alembic/versions/0003_fix_user_id_types.py"
    if out_path.exists():
        print(f"  [skip] migration از قبل وجود دارد: {out_path.name}")
        return
    content = MIGRATION_TEMPLATE.format(date=datetime.date.today().isoformat())
    write(out_path, content)
    print(f"  [ok] migration ساخته شد: {out_path.relative_to(REPO)}")
    print("  ⚠️  توجه: چون داده‌ی UUID قدیمی قابل نگاشت مستقیم به Integer نیست،")
    print("      این migration مقدار قبلی را NULL می‌کند. اگر داده‌ی واقعی")
    print("      در پروداکشن دارید، قبل از اجرا یک استراتژی migrate داده بنویسید.")


if __name__ == "__main__":
    fix_scenario_router()
    fix_scenario_models()
    fix_runs_router_and_model()
    add_migration()
    print("\n✅ اسکریپت ۱ کامل شد. یادتان نرود: alembic upgrade head")
