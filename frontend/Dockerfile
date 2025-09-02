# Node.jsベースのイメージを利用
FROM node:20-alpine

WORKDIR /app

# 依存関係インストール
COPY package*.json ./
RUN npm install

# ソースコードコピー
COPY . .

# 開発用 (Viteのホットリロード)
# CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
