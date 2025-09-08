<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useQuizStore } from "../stores/quiz"

const router = useRouter()
const quizStore = useQuizStore()

const currentIndex = ref(0)

// ストアの回答を初期化（初回のみ）
onMounted(() => {
    if (quizStore.questions.length === 0) {
        quizStore.fetchQuestions()
    }
})

// 現在の質問
const currentQuestion = computed(() => quizStore.questions[currentIndex.value])
// 進捗率
const progress = computed(() => ((currentIndex.value + 1) / quizStore.questions.length) * 100)

// 選択肢をクリックしたら次へ
const selectAnswer = (choiceId: number) => {
    quizStore.setAnswer(currentQuestion.value.id, choiceId)

    if (currentIndex.value < quizStore.questions.length - 1) {
        currentIndex.value++
    } else {
        router.push('/confirm')
    }
}

const goBack = () => {
    if (currentIndex.value > 0) currentIndex.value--
}

const isSelected = (choiceId: number) => {
    return quizStore.getAnswer(currentQuestion.value.id) === choiceId
}
</script>

<template>
    <div v-if="quizStore.questions.length > 0" class="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
        <!-- 進捗バー -->
        <div class="w-full max-w-xl mb-6">
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                class="h-full bg-green-600 transition-all"
                :style="{ width: `${progress}%` }"
                ></div>
            </div>
            <p class="text-sm text-gray-600 mt-2 text-right">
                {{ currentIndex + 1 }} / {{ quizStore.questions.length }}
            </p>
        </div>

        <!-- 質問 -->
        <h2 class="text-xl font-semibold mb-6 text-center text-gray-600">
            {{ currentQuestion.text }}
        </h2>

        <!-- 選択肢 -->
        <div class="grid gap-4 w-full max-w-md">
            <button
                v-for="choice in currentQuestion.choices"
                :key="choice.id"
                class="px-4 py-3 border rounded-xl shadow transition"
                :class="isSelected(choice.id) ? 'bg-green-500 text-white' : 'bg-white hover:bg-green-50 text-green-800'"
                @click="selectAnswer(choice.id)"
            >
                {{ choice.text }}
            </button>
        </div>

        <!-- 戻るボタン（2問目以降のみ） -->
        <div v-if="currentIndex > 0" class="mt-6">
            <button
                @click="goBack"
                class="px-4 py-2 bg-gray-300 rounded-xl text-gray-500 hover:bg-gray-400 transition"
            >
                ← 前の質問へ戻る
            </button>
        </div>
    </div>
    <div v-else>
        <p class="text-center text-gray-600 mt-20">質問が存在しません。最初からやり直してください。</p>
    </div>
</template>

<style scoped>
</style>