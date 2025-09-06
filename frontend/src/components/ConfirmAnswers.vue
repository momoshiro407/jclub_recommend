<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { Question, useQuizStore } from "../stores/quiz"

const quizStore = useQuizStore()
const router = useRouter()

// 修正対象の質問index（null ならモーダル非表示）
const editingId = ref<number | null>(null)

// IDから質問を取得
const getQuestion = (id: number) => {
    return quizStore.questions.find(q => q.id === id)
}

// 質問IDに対応する回答を取得
const getAnswer = (question: Question) => {
    const answer = quizStore.answers.find(a => a.questionId === question.id)
    return question.choices.find(c => c.id === answer.choiceId).text || '未回答'
}

const isSelected = (choiceId: number) => {
    const answer = quizStore.answers.find(a => a.questionId === editingId.value)
    return answer.choiceId === choiceId
}

// 修正モーダルを開く
const openEditModal = (questionId: number) => {
    editingId.value = questionId
}

// 修正を確定
const selectAnswer = (choiceId: number) => {
    if (editingId.value !== null) {
        quizStore.setAnswer(editingId.value, choiceId)
        editingId.value = null // モーダルを閉じる
    }
}

// 結果ページへ遷移
const goToResult = () => {
    router.push('/result')
}
</script>

<template>
    <div v-if="quizStore.questions.length > 0"  class="min-h-screen bg-gray-50 p-6 flex flex-col items-center">
        <h2 class="text-2xl font-bold mb-6 text-gray-600">回答内容の確認</h2>

        <!-- 回答一覧 -->
        <div class="w-full max-w-2xl space-y-4 flex-1">
            <div
                v-for="question in quizStore.questions"
                :key="question.id"
                class="bg-white rounded-xl shadow p-4 flex justify-between items-center"
            >
                <div class="text-gray-600">
                    <p class="font-semibold">Q{{ question.id }}. {{ question.text }}</p>
                    <p>A. {{ getAnswer(question) }}</p>
                </div>
                <button
                class="text-sm px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                @click="openEditModal(question.id)"
                >
                修正する
                </button>
            </div>
        </div>

        <!-- 結果ページへ進む -->
        <div class="w-full max-w-2xl mt-8">
            <button
                class="w-full py-3 text-lg font-semibold bg-green-600 text-white rounded-xl shadow hover:bg-green-700"
                @click="goToResult"
            >
                結果を見る
            </button>
        </div>

        <!-- 修正モーダル -->
        <div v-if="editingId !== null" class="fixed inset-0 bg-gray-500/50 flex items-center justify-center">
            <div class="bg-white p-6 rounded-2xl shadow-xl w-full max-w-md">
                <h3 class="text-lg font-bold mb-4 text-gray-600">
                    Q{{ editingId }}. {{ getQuestion(editingId).text }}
                </h3>
                <div class="space-y-2">
                    <button
                        v-for="choice in getQuestion(editingId).choices"
                        :key="choice.id"
                        class="w-full px-4 py-2 rounded-lg border shadow-sm transition"
                        :class="isSelected(choice.id) ? 'bg-green-500 text-white' : 'bg-white hover:bg-green-50 text-green-800'"
                        @click="selectAnswer(choice.id)"
                    >
                        {{ choice.text }}
                </button>
                </div>
                <button
                class="mt-4 px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
                @click="editingId = null"
                >
                    キャンセル
                </button>
            </div>
        </div>
    </div>
    <div v-else>
        <p class="text-center text-gray-600 mt-20">質問が存在しません。最初からやり直してください。</p>
    </div>
</template>
