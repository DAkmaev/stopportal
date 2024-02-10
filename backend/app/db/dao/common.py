from fastapi import HTTPException


async def update_registry_field(
    session, model, field_name, updated_fields, registry_item, error_message
):
    data = updated_fields.pop(field_name, None)
    current_value = getattr(registry_item, field_name)
    if data is not None and (
        current_value is None or data["id"] != getattr(registry_item, field_name).id
    ):
        item = await session.get(model, data["id"])
        if not item:
            raise HTTPException(status_code=404, detail=error_message)
        setattr(registry_item, field_name, item)
    elif data is None and current_value is not None:
        setattr(registry_item, field_name, None)
