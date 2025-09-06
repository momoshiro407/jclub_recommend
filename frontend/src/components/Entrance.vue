<script setup lang="ts">
// 特にロジック不要（静的ページ）
// ここではスタートボタンのルーティングのみ
</script>

<template>
    <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-8">
        <h1 class="text-4xl font-bold mb-6 text-green-700">
            Jリーグクラブ診断
        </h1>
        <p class="text-lg text-gray-700 mb-8 text-center max-w-xl">
            簡単な質問に答えるだけで、あなたにぴったりのJリーグクラブを診断します！
        </p>
        <router-link
            to="/questions"
            class="px-6 py-3 bg-green-600 text-white rounded-xl shadow-md hover:bg-green-700 transition"
        >
            診断を始める
        </router-link>
    </div>
</template>

<style scoped>
/* 必要に応じてカスタムCSS */
</style>
