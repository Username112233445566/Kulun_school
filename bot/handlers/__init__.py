from .common import router as common_router
from .student import router as student_router
from .teacher import router as teacher_router
from .admin_main import router as admin_main_router
from .admin_users import router as admin_users_router
from .admin_groups import router as admin_groups_router
from .admin_sync import router as admin_sync_router
from .admin_creation import router as admin_creation_router
from .admin_subjects import router as admin_subjects_router
from .admin_schedule import router as admin_schedule_router

__all__ = [
    'common_router',
    'student_router',
    'teacher_router',
    'admin_main_router',
    'admin_users_router',
    'admin_groups_router',
    'admin_sync_router',
    'admin_creation_router',
    'admin_subjects_router',
    'admin_schedule_router'
]