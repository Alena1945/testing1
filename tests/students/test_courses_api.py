import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Course, Student


class Client(APIClient):
    url = '/api/v1/courses/'

    def get_course(self, pk, **kwargs):
        return self.get(f'{self.url}{pk}/', **kwargs)

    def get_course_list(self, **kwargs):
        return self.get(f'{self.url}', **kwargs)

    def add_course(self, load_data):
        return self.post(self.url, data=load_data)

    def update_course(self, course_id, update_data):
        return self.patch(f'{self.url}{course_id}/', data=update_data)

    def delete_course(self, course_id):
        return self.delete(f'{self.url}{course_id}/')


@pytest.fixture
def api_client():
    return Client()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_one_course(api_client, course_factory):
    course = course_factory()
    response = api_client.get_course(str(course.id))
    data = response.json()

    assert response.status_code == 200
    assert data['id'] == course.id
    assert data['name'] == course.name


@pytest.mark.django_db
def test_get_course_list(api_client, course_factory):
    courses = course_factory(_quantity=10)
    response = api_client.get_course_list()
    data = response.json()

    assert response.status_code == 200
    assert len(data) == len(courses)
    for i, course in enumerate(courses):
        assert data[i]['id'] == course.id
        assert data[i]['name'] == course.name


@pytest.mark.django_db
def test_id_filter(api_client, course_factory):
    courses = course_factory(_quantity=10)
    for course in courses:
        params = {'id': course.id}
        response = api_client.get_course_list(data=params)
        data = response.json()

        assert response.status_code == 200
        assert data[0]['id'] == course.id
        assert data[0]['name'] == course.name


@pytest.mark.django_db
def test_name_filter(api_client, course_factory):
    courses = course_factory(_quantity=10)
    for course in courses:
        params = {'name': course.name}
        response = api_client.get_course_list(data=params)
        data = response.json()

        assert response.status_code == 200
        assert data[0]['id'] == course.id
        assert data[0]['name'] == course.name


@pytest.mark.django_db
def test_create_course(api_client):
    load_data = {"name": "python-dev"}
    post = api_client.add_course(load_data)
    get = api_client.get_course_list()
    get_data = get.json()

    assert post.status_code == 201
    assert get.status_code == 200
    assert get_data[0]['name'] == load_data['name']


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    course = course_factory()
    update_data = {"name": "fullstack"}
    update = api_client.update_course(course.id, update_data)
    response = api_client.get_course(course.id)
    data = response.json()

    assert update.status_code == 200
    assert data['id'] == course.id
    assert data['name'] == update_data['name']


@pytest.mark.django_db
def test_destroy_course(api_client, course_factory):
    course = course_factory()
    before = api_client.get_course_list()
    destroy = api_client.delete_course(course.id)
    after = api_client.get_course_list()
    deleted_course = api_client.get_course(course.id)

    assert destroy.status_code == 204
    assert deleted_course.status_code == 404
    assert len(before.data) == len(after.data) + 1
