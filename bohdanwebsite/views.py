import gzip
import threading
import cv2
from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView

from .models import Category, Post
from .forms import PostForm,EditForm
from django.urls import reverse_lazy,reverse
from django.http import HttpResponseRedirect, StreamingHttpResponse
#def home(request):
#    return render(request,'home.html',{})
 
def LikeView(request,pk):
    post = Post.objects.get(id=pk)
    #post = get_object_or_404(Post,id=request.POST.get('post_id'))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
         post.likes.add(request.user)
         liked = True
    
    return HttpResponseRedirect(reverse('article-detail',args=[str(pk)]))
    
class HomeView(ListView):
    model = Post
    template_name = 'home.html'
    #ordering = ['-post_date']
    ordering = ['-id']

    def get_context_data(self,*args,**kwargs):
        cat_menu = Category.objects.all()
        context = super(HomeView,self).get_context_data(*args,**kwargs)
        context["cat_menu"] = cat_menu
        return context

def CategoryView(request,cats):
    category_posts = Post.objects.filter(category=cats.replace('-',' '))
    return render(request,'categories.html',{'cats':cats.title().replace('-',' '),'category_posts':category_posts})

def CategoryListView(request):
    cat_menu_list = Category.objects.all()
    return render(request,'category_list.html',{'cat_menu_list':cat_menu_list })
    

class ArticleDetailView(DetailView):
    model = Post
    template_name = 'article-details.html'
    
    def get_context_data(self,*args,**kwargs):
        cat_menu = Category.objects.all()
        context = super(DetailView,self).get_context_data(*args,**kwargs)
        
        stuff = get_object_or_404(Post,id=self.kwargs['pk'])
        total_likes = stuff.total_likes()
        
        liked = False
        
        if stuff.likes.filter( id=self.request.user.id).exists(): # type: ignore                
            liked= True
        
        context["cat_menu"] = cat_menu
        context["total_likes"] = total_likes
        context["liked"] = liked
        return context
    
class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'add_post.html'
    
    def get_context_data(self,*args,**kwargs):
        cat_menu = Category.objects.all()
        context = super(CreateView,self).get_context_data(*args,**kwargs)
        context["cat_menu"] = cat_menu
        return context
    
    #fields = '__all__'
    #fields = ('title','body')

class AddCategoryView(CreateView):
    model = Category
    #form_class = PostForm
    template_name = 'add_category.html'
    fields = '__all__'
    def get_context_data(self,*args,**kwargs):
        cat_menu = Category.objects.all()
        context = super(AddCategoryView,self).get_context_data(*args,**kwargs)
        context["cat_menu"] = cat_menu
        return context
    #fields = '__all__'
    #fields = ('title','body')
     
class UpdatePostView(UpdateView):
    model = Post
    form_class = EditForm
    template_name='update_post.html'
    #fields=['title','title_tag','body']
    def get_context_data(self,*args,**kwargs):
        cat_menu = Category.objects.all()
        context = super(UpdatePostView,self).get_context_data(*args,**kwargs)
        context["cat_menu"] = cat_menu
        return context
#class UpdatePostView2(UpdateView):
    #model = Post
    #form_class = PostForm
    #template_name='update_post.html'

class DeletePostView(DeleteView):
    model = Post
    template_name='delete_post.html'
    success_url = reverse_lazy('home')

 
def Recognition(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type = "multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request,'recognition.html')

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed,self.frame) = self.video.read()
        threading.Thread(target = self.update,args = ()).start()
    
    def __del__(self):
        self.video.release()
        
    def get_frame(self):
        image = self.frame
        _,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()
        
    def update(self):
        while True:
            (self.grabbed,self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'+ frame +b'\r\n\r\n')
    
    