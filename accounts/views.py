from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import User, Session  
from .utils import hash_password, check_password, create_session, extract_face_encoding,find_user_by_face,detect_face_in_image
from django.contrib import messages
import os
from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.base import ContentFile

def landing_page(request):
    return render(request, 'landingpage.html')

def login_signup(request):
    # signup 
    if request.method == 'POST':
        if 'signup' in request.POST:
            data = request.POST
            if data['password'] != data['confirm_password']:
                return JsonResponse({'message': 'Passwords do not match'})
            

            image_data = data.get('captured_image')
            image_file = None
            ext = None  # Default to None
            encoding = extract_face_encoding(image_data)
            if encoding is None:
                messages.error(request, "No face detected in the image")
                return redirect('login-signup')
                
            if image_data:
                format, imgstr = image_data.split(';base64,')  
                ext = format.split('/')[-1]  # Set the image extension
                image_file = ContentFile(base64.b64decode(imgstr), name=f"{data['username']}_profile.{ext}")
            users = User.objects.filter(status=True)
            matched_user  = find_user_by_face(image_data, users)
            if matched_user:
                messages.error(request, 'user already registered! (image)')
                return redirect('login-signup')
            
            # Check if an image was uploaded before trying to save it
            user = User.objects.create(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            cnic=data['cnic'],
            user_image=image_file if image_file else None,
            face_encoding=encoding
            )

            if ext:
                user_image_path = os.path.join(settings.MEDIA_ROOT, f"user_images/{data['username']}_profile.{ext}")
                print(f"Image saved at: {user_image_path}")
            
            messages.success(request, "Registration successful!")
            return redirect('login-signup')
        # image login 
        if 'login' in request.POST:
            data = request.POST
            image_data = data['captured_image']
            users = User.objects.filter(status=True)
            matched_user  = find_user_by_face(image_data, users)
            if matched_user:
                token = create_session(matched_user)
                request.session['user_id'] = matched_user.id
                request.session['token'] = token
                return redirect('dashboard-page')
            else:
                messages.error(request, "Face not recognized or no matching user found.")
                return redirect('login-signup')
        
        # # login 
        # if 'login' in request.POST:
        #     data = request.POST
        #     try:
        #         # user = User.objects.get(username=data['username'])
        #         image_data = data['captured_image']
        #         if not user.status:
        #             messages.error(request, "user id inactive")
        #             return redirect('login-signup') 
        #         if check_password(data['password'], user.password_hash):
        #             token = create_session(user)
        #             request.session['user_id'] = user.id
        #             request.session['token'] = token
        #             print(request.session.get('token'))
        #             # messages.success(request, "Login successful!")
        #             return redirect('dashboard-page')  
        #             # return JsonResponse({'token': token})
        #     except User.DoesNotExist:
        #         messages.error(request, "user does not exist")
        #         return redirect('login-signup')  
        #     return JsonResponse({'error': 'Invalid credentials'}, status=401)
    
    return render(request, 'login-signup.html')





def logout(request):
    token = request.session.get('token')
    
    if token:
        Session.objects.filter(session_token=token).update(is_active=False)

    request.session.flush()
    messages.success(request, 'Logout successful')
    return redirect('login-signup')
def deactive(request):
    user_id = request.session.get('user_id')
    token = request.session.get('token')

    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user.status = False
            user.save()

            # Mark all sessions as inactive
            Session.objects.filter(user=user).update(is_active=False)

            request.session.flush()
            messages.success(request, 'Account deactivated and logged out successfully.')

        except User.DoesNotExist:
            messages.error(request, 'User not found.')

    return redirect('login-signup')
def dashboard(request):
    user_id = request.session.get('user_id')
    token = request.session.get('token')

    if user_id and token:
        try:
            session = Session.objects.get(session_token=token, is_active=True)
            user = session.user
            return render(request, 'dashboard.html', {'user': user})
        except Session.DoesNotExist:
            messages.error(request, 'Session expired or invalid.')
            request.session.flush()
            return redirect('login-signup')
    else:
        return redirect('login-signup')

