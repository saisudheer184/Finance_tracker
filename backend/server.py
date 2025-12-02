from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import bcrypt
import jwt
from decimal import Decimal
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Upload directory
UPLOAD_DIR = ROOT_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

# ============= MODELS =============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str
    user: User

class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str  # 'income' or 'expense'
    amount: float
    category: str
    description: str
    date: str
    receipt_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TransactionCreate(BaseModel):
    type: str
    amount: float
    category: str
    description: str
    date: str

class Budget(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    month: int
    year: int
    category: str
    amount: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BudgetCreate(BaseModel):
    month: int
    year: int
    category: str
    amount: float

# ============= AUTH HELPERS =============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    return jwt.encode({'user_id': user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return decode_token(credentials.credentials)

# ============= AUTH ROUTES =============

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(email=user_data.email, name=user_data.name)
    user_dict = user.model_dump()
    user_dict['password_hash'] = hash_password(user_data.password)
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    
    # Create token
    token = create_token(user.id)
    return Token(token=token, user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    # Find user
    user_dict = await db.users.find_one({"email": login_data.email})
    if not user_dict or not verify_password(login_data.password, user_dict['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Convert to User model
    if isinstance(user_dict['created_at'], str):
        user_dict['created_at'] = datetime.fromisoformat(user_dict['created_at'])
    
    user = User(**user_dict)
    token = create_token(user.id)
    return Token(token=token, user=user)

@api_router.get("/auth/me", response_model=User)
async def get_me(user_id: str = Depends(get_current_user)):
    user_dict = await db.users.find_one({"id": user_id})
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user_dict['created_at'], str):
        user_dict['created_at'] = datetime.fromisoformat(user_dict['created_at'])
    
    return User(**user_dict)

# ============= TRANSACTION ROUTES =============

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate, user_id: str = Depends(get_current_user)):
    transaction = Transaction(**transaction_data.model_dump(), user_id=user_id)
    transaction_dict = transaction.model_dump()
    transaction_dict['created_at'] = transaction_dict['created_at'].isoformat()
    
    await db.transactions.insert_one(transaction_dict)
    return transaction

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(user_id: str = Depends(get_current_user), type: Optional[str] = None):
    query = {"user_id": user_id}
    if type:
        query["type"] = type
    
    transactions = await db.transactions.find(query, {"_id": 0}).sort("date", -1).to_list(1000)
    
    for t in transactions:
        if isinstance(t['created_at'], str):
            t['created_at'] = datetime.fromisoformat(t['created_at'])
    
    return transactions

@api_router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str, user_id: str = Depends(get_current_user)):
    transaction = await db.transactions.find_one({"id": transaction_id, "user_id": user_id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if isinstance(transaction['created_at'], str):
        transaction['created_at'] = datetime.fromisoformat(transaction['created_at'])
    
    return Transaction(**transaction)

@api_router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction_data: TransactionCreate, user_id: str = Depends(get_current_user)):
    existing = await db.transactions.find_one({"id": transaction_id, "user_id": user_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = transaction_data.model_dump()
    await db.transactions.update_one({"id": transaction_id}, {"$set": update_data})
    
    updated = await db.transactions.find_one({"id": transaction_id}, {"_id": 0})
    if isinstance(updated['created_at'], str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    
    return Transaction(**updated)

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, user_id: str = Depends(get_current_user)):
    result = await db.transactions.delete_one({"id": transaction_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted"}

# ============= BUDGET ROUTES =============

@api_router.post("/budgets", response_model=Budget)
async def create_budget(budget_data: BudgetCreate, user_id: str = Depends(get_current_user)):
    # Check if budget already exists for this category/month/year
    existing = await db.budgets.find_one({
        "user_id": user_id,
        "category": budget_data.category,
        "month": budget_data.month,
        "year": budget_data.year
    })
    
    if existing:
        # Update existing
        await db.budgets.update_one(
            {"id": existing["id"]},
            {"$set": {"amount": budget_data.amount}}
        )
        updated = await db.budgets.find_one({"id": existing["id"]}, {"_id": 0})
        if isinstance(updated['created_at'], str):
            updated['created_at'] = datetime.fromisoformat(updated['created_at'])
        return Budget(**updated)
    
    budget = Budget(**budget_data.model_dump(), user_id=user_id)
    budget_dict = budget.model_dump()
    budget_dict['created_at'] = budget_dict['created_at'].isoformat()
    
    await db.budgets.insert_one(budget_dict)
    return budget

@api_router.get("/budgets", response_model=List[Budget])
async def get_budgets(user_id: str = Depends(get_current_user), month: Optional[int] = None, year: Optional[int] = None):
    query = {"user_id": user_id}
    if month:
        query["month"] = month
    if year:
        query["year"] = year
    
    budgets = await db.budgets.find(query, {"_id": 0}).to_list(1000)
    
    for b in budgets:
        if isinstance(b['created_at'], str):
            b['created_at'] = datetime.fromisoformat(b['created_at'])
    
    return budgets

@api_router.delete("/budgets/{budget_id}")
async def delete_budget(budget_id: str, user_id: str = Depends(get_current_user)):
    result = await db.budgets.delete_one({"id": budget_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted"}

# ============= REPORT ROUTES =============

@api_router.get("/reports/summary")
async def get_summary(user_id: str = Depends(get_current_user), month: Optional[int] = None, year: Optional[int] = None):
    query = {"user_id": user_id}
    
    # Filter by month/year if provided
    if month and year:
        # Create date range for the month
        from datetime import datetime
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        query["date"] = {"$gte": start_date, "$lt": end_date}
    
    # Get all transactions
    transactions = await db.transactions.find(query, {"_id": 0}).to_list(10000)
    
    # Calculate totals
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    total_savings = total_income - total_expense
    
    # Category breakdown
    category_breakdown = {}
    for t in transactions:
        if t['type'] == 'expense':
            category = t['category']
            category_breakdown[category] = category_breakdown.get(category, 0) + t['amount']
    
    # Top 5 spending categories
    top_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_savings": total_savings,
        "category_breakdown": category_breakdown,
        "top_categories": [{
            "category": cat,
            "amount": amt
        } for cat, amt in top_categories]
    }

@api_router.get("/reports/monthly")
async def get_monthly_report(user_id: str = Depends(get_current_user)):
    # Get last 6 months of data
    from datetime import datetime, timedelta
    transactions = await db.transactions.find({"user_id": user_id}, {"_id": 0}).to_list(10000)
    
    # Group by month
    monthly_data = {}
    for t in transactions:
        # Parse date (YYYY-MM-DD format)
        date_parts = t['date'].split('-')
        if len(date_parts) >= 2:
            month_key = f"{date_parts[0]}-{date_parts[1]}"
            if month_key not in monthly_data:
                monthly_data[month_key] = {"income": 0, "expense": 0}
            
            if t['type'] == 'income':
                monthly_data[month_key]['income'] += t['amount']
            else:
                monthly_data[month_key]['expense'] += t['amount']
    
    # Convert to list and sort
    result = []
    for month_key in sorted(monthly_data.keys(), reverse=True)[:6]:
        result.append({
            "month": month_key,
            "income": monthly_data[month_key]['income'],
            "expense": monthly_data[month_key]['expense'],
            "savings": monthly_data[month_key]['income'] - monthly_data[month_key]['expense']
        })
    
    return result[::-1]  # Reverse to show oldest first

# ============= UPLOAD ROUTE =============

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    # Generate unique filename
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"file_url": f"/uploads/{unique_filename}"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
