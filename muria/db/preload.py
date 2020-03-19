"""Some preloads of database content."""

tables = list()

roles = list()
roles.append({"id": 1, "name": "administrator"})
roles.append({"id": 2, "name": "contributor"})
roles.append({"id": 3, "name": "staff"})
roles.append({"id": 4, "name": "parent"})
roles.append({"id": 5, "name": "caretaker"})
roles.append({"id": 6, "name": "student"})

tables.append({"model": "Role", "data": roles})

responsibilities = list()
responsibilities.append({"id": 1, "name": "manager"})
responsibilities.append({"id": 2, "name": "user"})
responsibilities.append({"id": 3, "name": "journalist"})

tables.append({"model": "Responsibility", "data": responsibilities})

sets = list()

responsibility_role = [
    (1, 1),
    (1, 3),
    (2, 1),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (3, 2),
    (3, 3),
    (3, 6),
]

sets.append(
    {
        "parent": "Responsibility",
        "rel": "roles",
        "child": "Role",
        "data": responsibility_role,
    }
)
