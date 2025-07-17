import re
import json
from typing import Dict, List, Tuple, Optional, Union, Any
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForQuestionAnswering,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
    DataCollatorWithPadding
)
import torch
from torch.nn.functional import softmax
import numpy as np
from dataclasses import dataclass
from enum import Enum
from .models import Exercise, Muscle, Equipment, MovementType, CalorieEntry, Workout, DailyLog
