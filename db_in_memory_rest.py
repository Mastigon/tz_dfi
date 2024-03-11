from fastapi import FastAPI, HTTPException
from uuid import uuid4
from copy import deepcopy

app = FastAPI()


class DB:
    def __init__(self):
        self.data = {}

    def insert(self, value):
        new_id = str(uuid4())
        self.data[new_id] = value
        return new_id

    def select(self):
        return [{"id": id_, "value": value} for id_, value in self.data.items()]

    def delete(self, id_):
        if id_ in self.data:
            del self.data[id_]
            return True
        return False


class TransactionManager:
    def __init__(self, db):
        self.db = db
        self.transaction_stack = []

    def begin(self):
        if self.transaction_stack:
            current_state = deepcopy(self.transaction_stack[-1][-1])
        else:
            current_state = deepcopy(self.db.data)
        if not self.transaction_stack or self.transaction_stack[-1] == []:
            self.transaction_stack.append([current_state])
        else:
            self.transaction_stack[-1].append(current_state)

    def commit(self):
        if self.transaction_stack and self.transaction_stack[-1]:
            self.transaction_stack[-1].pop()
            if not self.transaction_stack[-1]:
                self.transaction_stack.pop()
            if not self.transaction_stack:
                self.db.data = deepcopy(self.transaction_stack[-1][-1])
        else:
            raise ValueError("No transaction to commit")

    def rollback(self):
        if self.transaction_stack and self.transaction_stack[-1]:
            last_saved_state = self.transaction_stack[-1].pop()
            self.db.data = deepcopy(last_saved_state)
            if not self.transaction_stack[-1]:
                self.transaction_stack.pop()
        else:
            raise ValueError("No transaction to rollback")


db = DB()
tm = TransactionManager(db)

@app.get("/select")
def select():
    return db.select()

@app.post("/insert")
def insert(value: str):
    return {"id": db.insert(value)}

@app.delete("/delete/{id_}")
def delete(id_: str):
    success = db.delete(id_)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"success": True}

@app.post("/begin")
def begin_transaction():
    tm.begin()
    return {"success": True}

@app.post("/commit")
def commit_transaction():
    try:
        tm.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}

@app.post("/rollback")
def rollback_transaction():
    try:
        tm.rollback()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}

