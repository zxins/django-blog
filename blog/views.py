from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from comments.forms import CommentForm
from blog.models import Post, Category

from django.views.generic import ListView, DetailView
import markdown



# 主页的类视图
class IndexView(ListView):
	model = Post
	template_name = 'blog/index.html'
	context_object_name = 'post_list'



# 文章
class PostDetailView(DetailView):
    # 这些属性的含义和 ListView 是一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        post.body = markdown.markdown(post.body,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                      ])
        return post

    def get_context_data(self, **kwargs):
        # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），
        # 还要把评论表单、post 下的评论列表传递给模板。
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context

# 归档的类视图
class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
                                                               created_time__month=month
                                                               )


# 分类的类视图
class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)

#############################################################################
# 主页的视图函数
def index(request):

	post_list = Post.objects.all()
	return render(request, 'blog/index.html', context={'post_list': post_list})

# 文章详情
# 参数pk用于接收文章id(对应models.Post下的get_absolute_url方法) 并作为url使用
def detail(request, pk):

	# 当传入的pk对应的Post在数据库存在时，返回对应的post; 不存在，返回404错误
	post = get_object_or_404(Post, pk=pk)

	# 阅读量 +1
	post.increase_views()

	# markdown
	post.body = markdown.markdown(post.body, extensions=['markdown.extensions.extra', 
														'markdown.extensions.codehilite', 
														'markdown.extensions.toc'
														])

	# 评论 表单
	form = CommentForm()
	# 获取当前 post 下的全部评论
	comment_list = post.comment_set.all()

	# 将文章、表单、评论列表 作为模板变量传给detail.html模板,以便渲染相应数据
	context = {	'post': post,
				'form': form,
				'comment_list': comment_list,
				}

	return render(request, 'blog/detail.html', context=context)

# 归档的视图函数
def archives(request, year, month):
	
	post_list = Post.objects.filter(created_time__year=year, 
									created_time__month=month
									)

	return render(request, 'blog/index.html', context={'post_list': post_list})



# 分类的视图函数
def category(request, pk):

	cate = get_object_or_404(Category, pk=pk)
	post_list = Post.objects.filter(category=cate)
	return render(request, 'blog/index.html', context={'post_list': post_list})