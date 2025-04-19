from typing import List, Union

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from sqlmodel import Session, or_, select

# ✅ استيراد الجلسة الافتراضية من قاعدة البيانات
from ..db import ActiveSession

# ✅ استيراد الدوال والنماذج الخاصة بالمستخدمين والصلاحيات
from ..security import (
    AdminUser,  # Dependency: يسمح فقط للمشرفين
    AuthenticatedFreshUser,  # Dependency: يسمح للمستخدمين الذين سجلوا دخولهم حديثاً
    AuthenticatedUser,  # Dependency: أي مستخدم مسجل دخول
    User,  # النموذج (SQLModel)
    UserCreate,  # بيانات المستخدم المطلوبة لإنشاء مستخدم جديد
    UserPasswordPatch,  # بيانات تعديل كلمة المرور
    UserResponse,  # الاستجابة النهائية
    get_current_user,  # الدالة التي تجلب المستخدم الحالي من الجلسة
    get_password_hash,  # دالة لتشفير كلمة المرور
)

router = APIRouter()

# ✅ عرض قائمة المستخدمين (فقط للمشرفين)
@router.get("/", response_model=List[UserResponse], dependencies=[AdminUser])
async def list_users(*, session: Session = ActiveSession):
    users = session.exec(select(User)).all()
    return users


# ✅ إنشاء مستخدم جديد (فقط للمشرفين)
@router.post("/", response_model=UserResponse, dependencies=[AdminUser])
async def create_user(*, session: Session = ActiveSession, user: UserCreate):

    # ✅ تأكد من عدم تكرار اسم المستخدم
    try:
        await query_user(session=session, user_id_or_username=user.username)
    except HTTPException:
        pass  # يعني المستخدم غير موجود = تمام
    else:
        raise HTTPException(status_code=422, detail="Username already exists")

    # ✅ تحويل البيانات إلى كائن SQLModel وتشفير كلمة المرور
    db_user = User.from_orm(user)
    db_user.password = get_password_hash(user.password)

    # ✅ حفظ المستخدم
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# ✅ تعديل كلمة مرور مستخدم (يجب أن يكون المستخدم هو نفسه أو مشرف)
@router.patch(
    "/{user_id}/password/",
    response_model=UserResponse,
    dependencies=[AuthenticatedFreshUser],
)
async def update_user_password(
    *,
    user_id: int,
    session: Session = ActiveSession,
    request: Request,
    patch: UserPasswordPatch,
):
    # ✅ جلب المستخدم من قاعدة البيانات
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ التحقق من أن المستخدم نفسه أو مشرف
    current_user: User = get_current_user(request=request)
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You can't update this user password"
        )

    # ✅ التحقق من تطابق كلمتي المرور
    if not patch.password == patch.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    # ✅ تحديث كلمة المرور بعد التشفير
    user.password = get_password_hash(patch.password)

    # ✅ حفظ التغييرات
    session.commit()
    session.refresh(user)
    return user


# ✅ عرض بيانات مستخدم معين (بالـ id أو username)
@router.get(
    "/{user_id_or_username}/",
    response_model=UserResponse,
    dependencies=[AuthenticatedUser],
)
async def query_user(
    *, session: Session = ActiveSession, user_id_or_username: Union[str, int]
):
    # ✅ استعلام عن المستخدم من قاعدة البيانات
    user = session.query(User).where(
        or_(
            User.id == user_id_or_username,
            User.username == user_id_or_username,
        )
    )

    if not user.first():
        raise HTTPException(status_code=404, detail="User not found")
    return user.first()


# ✅ حذف مستخدم (فقط للمشرفين)
@router.delete("/{user_id}/", dependencies=[AdminUser])
def delete_user(
    *, session: Session = ActiveSession, request: Request, user_id: int
):
    # ✅ جلب المستخدم
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Content not found")

    # ✅ التأكد أن المشرف لا يحذف نفسه
    current_user = get_current_user(request=request)
    if user.id == current_user.id:
        raise HTTPException(
            status_code=403, detail="You can't delete yourself"
        )

    # ✅ حذف المستخدم
    session.delete(user)
    session.commit()
    return {"ok": True}
