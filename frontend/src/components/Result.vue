<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useQuizStore } from "../stores/quiz"
import axios from "axios"

// 診断結果クラブ型
type ClubResult = {
    id: number;
    name: string;
    division: number;
    location: string;
    emblem: string;
    color: string;
    description: string;
    website_url: string;
    score: number; // 一致度（%）
}

const quizStore = useQuizStore()
const router = useRouter()
const loading = ref(true)
const results = ref<ClubResult[]>([])
// アニメーション用スコア
const animatedScores = ref<number[]>([])

onMounted(async () => {
    try {
        const res = await axios.post('http://localhost:5000/recommend/', { answers: quizStore.answers })
        results.value = res.data.results
        // スコア配列を0で初期化してから代入
        animatedScores.value = results.value.map(() => 0)
        results.value.forEach((club, idx) => {
            // アニメーション用に少し遅らせて表示
            setTimeout(() => {
                animatedScores.value[idx] = club.score
            }, 300 * idx)
        })
    } catch (err) {
        console.error('API呼び出し失敗:', err)
    } finally {
        loading.value = false
    }
})

// 詳細モーダル
const selectedClub = ref<ClubResult | null>(null)
const openModal = (club: ClubResult) => {
    selectedClub.value = club
}
const closeModal = () => {
    selectedClub.value = null
}

const restart = () => {
    quizStore.$reset()
    router.push('/')
}

</script>

<template>
    <div class="p-6 bg-gray-50 min-h-screen">
        <h1 class="text-3xl font-bold mb-6 text-center text-gray-600">あなたにおすすめのクラブ</h1>

        <div v-if="loading" class="text-center text-gray-600 mt-20">診断結果を計算中です…</div>
        <!-- 結果カード -->
        <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <div
                v-for="(club, idx) in results"
                :key="club.id"
                class="bg-white rounded-2xl shadow p-6 cursor-pointer hover:shadow-lg transition transform hover:scale-105"
                @click="openModal(club)"
            >
                <img :src="club.emblem" alt="emblem" class="w-16 h-16 mx-auto mb-4" />
                <h2 class="text-xl font-semibold text-center mb-2 text-gray-500">{{ club.name }}</h2>
                <p class="text-center text-sm text-gray-500 mb-4">
                一致度: {{ club.score }}%
                </p>
                <div class="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                        class="h-full transition-all duration-700 ease-out"
                        :style="{ width: animatedScores[idx] + '%', backgroundColor: club.color }"
                    ></div>
                </div>
            </div>
        </div>

        <!-- もう一回診断するボタン -->
        <div class="mt-6">
            <button @click="restart" class="px-4 py-2 bg-gray-300 rounded-xl text-gray-500 hover:bg-gray-400 transition">
                もう一度診断する
            </button>
        </div>

        <!-- 詳細モーダル -->
        <div v-if="selectedClub" class="fixed inset-0 bg-gray-500/50 flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl text-gray-500 shadow-lg max-w-lg w-full p-6 relative">
                <button class="absolute top-3 right-3 text-gray-500 hover:text-gray-800" @click="closeModal">✕</button>
                <img :src="selectedClub.emblem" alt="emblem" class="w-20 h-20 mx-auto mb-4"/>
                <h2 class="text-2xl font-bold text-center mb-4">{{ selectedClub.name }}</h2>
                <p class="mb-2">{{ selectedClub.location }}</p>
                <p class="mb-2">{{ selectedClub.description }}</p>
                <a :href="selectedClub.website" target="_blank" class="text-blue-600 underline">公式サイト</a>
            </div>
        </div>
    </div>
</template>
