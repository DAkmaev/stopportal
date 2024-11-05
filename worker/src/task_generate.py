def ta_generate_task(
    message_json: str,
):
    ta_message: TAGenerateMessage = TypeAdapter(TAGenerateMessage).validate_json(
        message_json,
    )
    return generate_decision(ta_message)