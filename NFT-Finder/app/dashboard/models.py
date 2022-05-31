#from mongoengine import Document, CASCADE, ValidationError
from fileinput import filename
import mongoengine as me
from flask_mongoengine import BaseQuerySet
#from .selenium_class import get, get_picture
#from app import db as me
from PIL import UnidentifiedImageError

BASE_USER_URL = 'https://rarible.com/user/'

class RaribleUser(me.Document):
    _id = me.StringField(required=True) # pk by default
    url = me.URLField()
    avatar_url = me.URLField()
    avatar = me.ImageField(size=(800, 600, True))
    followers = me.IntField(min_value=0, default=0)
    following = me.IntField(min_value=0, default=0)
    page_links = me.ListField(me.URLField())

    owned = me.IntField(min_value=0, default=1)
    sold = me.IntField(min_value=0, default=1)
    created = me.IntField(min_value=0, default=1)

    meta = {'allow_inheritance': True}

    def __repr__(self):
        return f'(Rarible user, id: {self._id})'

    def __str__(self):
        return f'(Rarible user, id: {self._id})'
    
    def clean(self):
        try:
            id_db = RaribleUser.objects.get(_id=self._id)
        except RaribleUser.DoesNotExist:
            id_db = None

        if id_db:
            raise me.ValidationError('Violated unique constrain, the id does already exist in the database.')
        if not self.url:
            self.url = BASE_USER_URL + self._id
        if self.url == BASE_USER_URL:
            raise me.ValidationError("User Id is invalid or has not been submitted.")


class Buyer(RaribleUser):
    owned = me.IntField(min_value=0, default=1)

class Seller(RaribleUser):
    sold = me.IntField(min_value=0, default=1)

class Creator(RaribleUser):
    created = me.IntField(min_value=0, default=1)

class User(me.Document):
    """
    
    -- name: username of a new created user
    -- password: encrypted password of a new user
    -- email: email in from .*@.*\\..*

    """
    name = me.StringField(required=True)
    password = me.StringField(required=True)
    email = me.EmailField(required=True)

    meta = {'queryset_class': BaseQuerySet}

    def clean(self):

        try:
            name_db = User.objects.get(name=self.name)
        except User.DoesNotExist:
            name_db = None

        try:
            email_db = User.objects.get(email=self.email)
        except User.DoesNotExist:
            email_db = None

        if name_db:
            raise me.ValidationError('The username already exists in the database')
        if email_db:
            raise me.ValidationError('The email is already in the system.')

class NftItem(me.Document):
    _id = me.StringField(required=True) # pk by default
    minted_at = me.DateTimeField()
    token_id = me.IntField()
    # time_minted = minted_at - datetime.now
    url = me.URLField()
    name = me.StringField()
    description = me.StringField()
    # picture = me.ImageField(size=(1920, 1080, True))
    filename = me.StringField()
    attr_string = me.StringField()
    # references to participated users
    creators = me.ListField(me.ReferenceField(RaribleUser, reverse_delete_rule=me.CASCADE))
    seller_id = me.ReferenceField(RaribleUser, reverse_delete_rule=me.CASCADE)
    buyer_id = me.ReferenceField(RaribleUser, reverse_delete_rule=me.CASCADE)
    # purchase info
    sold_date = me.DateTimeField(required=True)
    price = me.FloatField(required=True)
    currency = me.StringField(max_length=50, required=True)
    # dict with keys and values for an item
    # attributes = me.DictField(required=True)
    # additional info needed for validation
    # deleted = BooleanField(required=True)

    def __repr__(self):
        return f'(Rarible item, createdAt: {self.minted_at}, id: {self._id})'

    def __str__(self):
        return f'(Rarible item, createdAt: {self.minted_at}, id: {self._id})'

    def clean(self):
        try:
            id_db = NftItem.objects.get(_id=self._id)
        except NftItem.DoesNotExist:
            id_db = None

        if id_db:
            raise me.ValidationError(f'Violated unique constrain, the id {self._id} does already exist in the database.')
        else:
            if self.url:
                try:
                   avatar_img = 1
                except UnidentifiedImageError as err:
                    print(err)
                    avatar_img = None
                if avatar_img:
                    self.filename = avatar_img
                    filename_txt = avatar_img[: 12] + '.txt'
                    with open(filename_txt, 'w') as f:
                        try:
                            f.write(self.attr_string)
                        except UnicodeEncodeError as err:
                            print(err)
                            f.write("Default string")
                    #with open(avatar_img, 'rb') as img:
                    #    self.picture.put(img)
                else:
                    raise me.ValidationError(f'Picture for the item {self._id} could not be loaded.')
        
            #raise me.ValidationError('All submitted nft attributes should be key-value structured.')
        
class ItemAttribute(me.Document):
    """test_string"""
    # id will be automatically set
    item_id = me.ReferenceField(NftItem, required=True) # fk
    key = me.StringField(required=True)
    value = me.StringField(required=True)

    def clean(self):

        for attr in [self.key, self.value]:
            value_raw = str(attr).strip()
            # filter out special characters
            value_alnum = str(v for v in value_raw if v.isalnum())
            value_clean = ''.join(value_alnum.split())
            if len(value_clean) < 3 or value_clean.isnumeric():
                attr = None
            else:
                attr = value_clean