from rest_framework.test import APITestCase
from rest_framework import status
from .models import Boards, Columns, Cards
from users.models import User
from rest_framework.authtoken.models import Token

class CardMovementTestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(firstname='test', lastname='user', email='a@a.com' ,password='password123')
        self.client.login(email='a@a.com', password='password123')


        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.board = Boards.objects.create(title='Test Board', user=self.user)

        self.column1 = Columns.objects.create(title='To Do', board=self.board, order=1)
        self.column2 = Columns.objects.create(title='In Progress', board=self.board, order=2)

        self.card1 = Cards.objects.create(task='Card 1', column=self.column1, position=1)
        self.card2 = Cards.objects.create(task='Card 2', column=self.column1, position=2)

    def test_move_card_to_new_column(self):
        url = f'/cards/{self.card1.id}/move/'
        data = {
            'target_column_id': self.column2.id,
            'new_position': 1,
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.card1.refresh_from_db()

        self.assertEqual(self.card1.column, self.column2)
        self.assertEqual(self.card1.position, 1)

    def test_invalid_column(self):
        url = f'/cards/{self.card1.id}/move/'
        data = {
            'target_column_id': 999,
            'new_position': 1,
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_invalid_position(self):
        url = f'/cards/{self.card1.id}/move/'
        data = {
            'target_column_id': self.column2.id,
            'new_position': 'invalid',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
