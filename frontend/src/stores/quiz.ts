import { defineStore } from "pinia"
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
        // 初期化（モックの質問を投入）
        initQuestions() {
            this.questions = [
                {
                    id: 1,
                    text: "サッカー観戦のスタイルは？",
                    choices: [
                        { id: 1, text: "スタジアムで熱狂したい" },
                        { id: 2, text: "家でゆったり観たい" }
                    ]
                },
                {
                    id: 2,
                    text: "応援したいクラブの地域は？",
                    choices: [
                        { id: 1, text: "地元" },
                        { id: 2, text: "全国的に有名なクラブ" }
                    ]
                },
                {
                    id: 3,
                    text: "クラブに求めるものは？",
                    choices: [
                        { id: 1, text: "強さ" },
                        { id: 2, text: "親しみやすさ" }
                    ]
                }
            ]
            this.answers = this.questions.map(q => ({
                questionId: q.id,
                choiceId: null
            }))
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
