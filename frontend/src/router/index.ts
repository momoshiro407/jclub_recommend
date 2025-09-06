import { createRouter, createWebHistory } from 'vue-router'
import Entrance from '../components/Entrance.vue'
import Question from '../components/Question.vue'
import Result from '../components/Result.vue'
import ConfirmAnswers from '../components/ConfirmAnswers.vue'

const routes = [
    { path: '/', component: Entrance },
    { path: '/questions', component: Question },
    { path: '/confirm', component: ConfirmAnswers },
    { path: '/result', component: Result },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
