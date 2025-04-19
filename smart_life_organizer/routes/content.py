from typing import List, Union
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlmodel import Session, or_, select

from ..db import ActiveSession
from ..models.content import Content, ContentIncoming, ContentResponse
from ..security import AuthenticatedUser, User, get_current_user

router = APIRouter()

# ✅ جلب كل المحتويات (مفتوح للجميع)
@router.get("/", response_model=List[ContentResponse])
async def list_contents(*, session: Session = ActiveSession):
    contents = session.exec(select(Content)).all()
    return contents

# ✅ جلب محتوى محدد بالـ ID أو slug
@router.get("/{id_or_slug}/", response_model=ContentResponse)
async def query_content(
    *, id_or_slug: Union[str, int], session: Session = ActiveSession
):
    content = session.exec(
        select(Content).where(
            or_(
                Content.id == id_or_slug,
                Content.slug == id_or_slug,
            )
        )
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return content

# ✅ إنشاء محتوى جديد - يتطلب توثيق المستخدم
@router.post("/", response_model=ContentResponse, dependencies=[AuthenticatedUser])
async def create_content(
    *,
    session: Session = ActiveSession,
    request: Request,
    content: ContentIncoming,
):
    # ربط المحتوى بالمستخدم الحالي
    db_content = Content.from_orm(content)
    user: User = get_current_user(request=request)
    db_content.user_id = user.id

    session.add(db_content)
    session.commit()
    session.refresh(db_content)
    return db_content

# ✅ تعديل محتوى موجود - فقط من قبل المالك أو المدير
@router.patch("/{content_id}/", response_model=ContentResponse, dependencies=[AuthenticatedUser])
async def update_content(
    *,
    content_id: int,
    session: Session = ActiveSession,
    request: Request,
    patch: ContentIncoming,
):
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # التحقق من أن المستخدم يملك المحتوى أو مدير
    current_user: User = get_current_user(request=request)
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You don't own this content")

    # تطبيق التعديلات
    patch_data = patch.dict(exclude_unset=True)
    for key, value in patch_data.items():
        setattr(content, key, value)

    session.commit()
    session.refresh(content)
    return content

# ✅ حذف محتوى - فقط من قبل المالك أو المدير
@router.delete("/{content_id}/", dependencies=[AuthenticatedUser])
def delete_content(
    *,
    session: Session = ActiveSession,
    request: Request,
    content_id: int
):
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # التأكد من الصلاحية
    current_user = get_current_user(request=request)
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You don't own this content")

    session.delete(content)
    session.commit()
    return {"ok": True}