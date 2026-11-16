.descriptor.db.status
| select(.valid == true
    and (.built | type == "string" and length > 0)
    and (.schemaVersion | type == "string" and length > 0))
| [.built, .schemaVersion, .from]
