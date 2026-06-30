from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class MyAccountManager(BaseUserManager):
  def create_user(self, first_name, last_name, username, email, password=None):
      """
      Creates and saves a User with the given email, date of
      birth and password.
      """
      if not email:
          raise ValueError("Users must have an email address")
        
      if not username:
          raise ValueError("User must have an username")  

      user = self.model(
          email=self.normalize_email(email),
          username = username,
          first_name=first_name,
          last_name=last_name
      )

      user.set_password(password)
      user.save(using=self._db)
      return user
    
    

  def create_superuser(self, first_name, last_name, username, email, password=None):
      """
      Creates and saves a superuser with the given email, date of
      birth and password.
      """
      user = self.create_user(
          email = self.normalize_email(email),
          username=username,
          password=password,
          first_name=first_name,
          last_name=last_name
      )
      
      user.is_admin = True
      user.is_active = True
      user.is_staff = True
      user.is_superadmin = True
      user.save(using=self._db)
      return user


#Custom Accounts manager for Custom Authentication
class Account(AbstractBaseUser):
  first_name = models.CharField(max_length=50)
  last_name  = models.CharField(max_length=50)
  username   = models.CharField(max_length=50, unique=True)
  email      = models.EmailField(max_length=100, unique=True)
  phone_number = models.CharField(max_length=16)
  
  
  #Required Field from Django Auth module,
  date_joined = models.DateTimeField(auto_now_add=True)
  last_login = models.DateTimeField(auto_now_add=True)
  is_admin = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  is_active = models.BooleanField(default=False)
  is_superadmin = models.BooleanField(default=False)
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username','first_name','last_name']
  
  objects = MyAccountManager()
  
  def __str__(self):
    return self.email

  def full_name(self):
      return f"{self.first_name} {self.last_name}"
  
  def has_perm(self, perm, obj=None):
      "Does the user have a specific permission?"
      # Simplest possible answer: Yes, always
      return True

  def has_module_perms(self, app_label):
      "Does the user have permissions to view the app `app_label`?"
      # Simplest possible answer: Yes, always
      return True  

class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='userprofile', blank=True, null=True)
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"