from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher.filters import Text
from aiogram.types.message import ContentType
from aiogram.dispatcher import FSMContext

from data.config import DESCR, INSTRUCT, PREDOSTR
from data.keyboards import kb_free, kb_instruct, kb_reg, kb_unreg, kb_profile, kb_admin
from data.inline_keyboards import ikas, paykb, inl_kb_pr
from data.classes import Auth


import logging
import sqlite3
import csv
from datetime import date, timedelta, datetime, time
from cryptography.fernet import Fernet
from pybit.unified_trading import HTTP
from pybit import exceptions
from dotenv import load_dotenv
import calendar
import os