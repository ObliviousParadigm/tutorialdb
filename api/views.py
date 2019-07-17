from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import tutorialSerializer, tagSerializer, tutorialPOST
from django.shortcuts import render
from app.models import tutorial, tag
from django.utils import timezone
from taggie.parser import generateTags

 
# Just wraps a simple HTTP Response to a JSON Response
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@api_view(['GET'])
def index(request):
    return render(request, 'api.html')


@api_view(['GET'])
def tutorial_Tags(request, tags):
	"""
	Return tutorials with a {tag}
	"""
	tags = tags.split(',')
	customTutorials = tutorial.objects.filter(tags__name__in = tags).distinct()
	serializer = tutorialSerializer(customTutorials, many=True)
	return JSONResponse(serializer.data)

@api_view(['GET'])
def latest(request):
	"""
	Return latest 10 tutorials from tutorialdb
	"""
	results = tutorial.objects.all().order_by('-id')[:10]
	serializer = tutorialSerializer(results, many=True)
	return JSONResponse(serializer.data)


@api_view(['GET'])
def tutorial_Tags_Type(request, tags, ttype):
	"""
	Return tutorials with a {tag} and {type}
	"""
	tags = tags.split(',')
	ttype = ttype.split(',')
	customTutorials = tutorial.objects.filter(tags__name__in = tags, category__in = ttype).distinct()
	serializer = tutorialSerializer(customTutorials, many=True)
	return JSONResponse(serializer.data)


@api_view(['GET'])
def tags(request):
	"""
	Returns all tags

	"""
	tags = tag.objects.all()
	print(tags)
	serializer = tagSerializer(tags, many=True)
	return JSONResponse(serializer.data)

def filterTags(tags):
	print()

@api_view(['GET', 'POST'])
def tutorials(request):
	"""
	get: Returns all tutorials

	post: POST a tutorial
	"""
	if request.method == 'GET':
		tutorials = tutorial.objects.all()
		serializer = tutorialSerializer(tutorials, many=True)
		return JSONResponse(serializer.data)
	elif request.method == 'POST':
		postserializer = tutorialPOST(data = request.data)
		if postserializer.is_valid():
			# generated from my parser
			title, tagList = generateTags(request.data['link'])
			print(title)
			print(tagList)

			# this is woring fine
			tutorialObject = tutorial.objects.create(
				title=title, 
				link=request.data['link'], 
				category = request.data['category']
			)
			# this generates error
			tutorialObject.tags.set(tagList)

			return JSONResponse({"message " : "submitted" }, status=status.HTTP_202_ACCEPTED)
		return JSONResponse({"message":"not_valid"})