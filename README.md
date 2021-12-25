# Student project quizeApi
BackEnd API:
1. WordNet usage
2. Pymorphy2 usage
3. Testing
4. Json types
5. Flask

# No need to install
URL: http://courseproject.pythonanywhere.com/

# Queries:
## 1. /feedback - Post query for updating information about words and translation for user:
### Information
  - checking user
  - checkin words
  - update information (0 - unguessed word, 1 - guessed word)
  - create information
  - create tags for each new word ("rat": ["noun", "sing", "грызун"])
  - add tags to json
  
### Get json:
{"user_id_1": 
    {"word_1": 
        {"translation": "translation_1", 
        "result": 0},
    "word_2": 
        {"translation": "translation_2", 
        "result": 1}
    },
"user_id_2": 
    {"word_1": 
        {"translation": "translation_1", 
        "result": 0},
    "word_2": 
        {"translation": "translation_2", 
        "result": 1}
    }
}

### Example
{"118035761240671491565": 
    {"building": 
        {"translation": "здание", 
        "result": 0}
    }
}

## /getwords?code=code&option=option&amount=amount - Get query for get information and get all stats:
### Info:
Return one or several words by tags for nessecary code

### Usage:
 - code: user_id
 - option: tag for get quize ("noun", "sing" or "грызун"...)
 - amount: amount of words (0, 1, 5...)
 
### Example:
 - /getwords?code=12055025&option=грызун&amount=3
