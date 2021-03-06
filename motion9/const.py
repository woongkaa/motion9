# -*- coding: utf-8 -*-
# Constant (상수) 관련 value를 저장하는 file

ITEM_COUNT_PER_PAGE_FOR_PRODUCT = 6
ITEM_COUNT_PER_PAGE_FOR_SET = 6
ITEM_COUNT_PER_PAGE_MYPAGE_INTEREST_PRODUCT = 9
ITEM_COUNT_PER_PAGE_MYPAGE_INTEREST_SET = 6

PAGER_INDICATOR_LENGTH = 5

CODE_LOGIN_REQUIRED = 1
CODE_PARAMS_WRONG = 2
CODE_FACEBOOK_TOKEN_IS_NOT_VALID = 3
CODE_INTEGRITY_ERROR = 4

ERROR_CODE_AND_MESSAGE_DICT = {
    CODE_LOGIN_REQUIRED: 'login required',
    CODE_PARAMS_WRONG: 'params wrong',
    CODE_FACEBOOK_TOKEN_IS_NOT_VALID: 'facebook token is not valid',
    CODE_INTEGRITY_ERROR: 'integrity error'
}