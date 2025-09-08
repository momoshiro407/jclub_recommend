import { defineStore } from "pinia"
import axios from "axios"
import Question from "../components/Question.vue"

export type Choice = {
    id: number
    text: string
}

export type Question = {
    id: number
    text: string
    choices: Choice[]
}

export type Answer = {
    questionId: number
    choiceId: number | null
}

export const useQuizStore = defineStore('quiz', {
    state: () => ({
        questions: [] as Question[],
        answers: [] as Answer[],
    }),
    actions: {
        async fetchQuestions() {
            try {
                const res = await axios.get('http://localhost:5000/questions/')
                this.questions = res.data.questions
                // 質問に対応する回答を初期化
                this.answers = this.questions.map(q => ({
                    questionId: q.id,
                    choiceId: null
                }))
            } catch (err) {
                console.error('質問データの取得に失敗:', err)
            }
        },
        setAnswer(questionId: number, choiceId: number) {
            const answer = this.answers.find(a => a.questionId === questionId)
            if (answer) answer.choiceId = choiceId
        },
        getAnswer(questionId: number): number | null {
            const answer = this.answers.find(a => a.questionId === questionId)
            return answer ? answer.choiceId : null
        },
    }
})
