import Vue from 'vue'
import Router from 'vue-router'

import HomeOperator from '../views/HomeOperator'
import MyUsersOperator from '../views/MyUsersOperator'
import Contacts from '../views/Contacts'
import PageOne from '../views/PageOne'
import PageTwo from '../views/PageTwo'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeOperator
    },
    {
      path: '/campain/:campain',
      name: 'users',
      component: MyUsersOperator
    },
    {
      path: '/contacts',
      name: 'contacts',
      component: Contacts
    },
    {
      path: '/page_one',
      name: 'page_one',
      component: PageOne
    },
    {
      path: '/page_two',
      name: 'page_two',
      component: PageTwo
    }
  ]
})
