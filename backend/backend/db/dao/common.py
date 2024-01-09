from fastapi import HTTPException


async def update_registry_field(session, model, field_name, updated_fields,
                                registry_item, error_message):
    data = updated_fields.pop(field_name, None)
    if data is not None and data['id'] != getattr(registry_item, field_name).id:
        item = await session.get(model, data['id'])
        if not item:
            raise HTTPException(status_code=404, detail=error_message)
        setattr(registry_item, field_name, item)
