<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
    <!-- Navbar -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-100">
            AI
          </div>
          <div>
            <h1 class="text-base font-bold tracking-tight text-slate-900">ALIST-IMAGE-API</h1>
            <span class="text-[10px] text-indigo-600 font-semibold uppercase tracking-wider bg-indigo-50 px-1.5 py-0.5 rounded">v2.0 Pro</span>
          </div>
        </div>

        <div v-if="token" class="flex items-center gap-1 sm:gap-2">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id ? 'bg-indigo-50 text-indigo-600 font-semibold' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100',
              'px-3.5 py-2 rounded-xl text-sm transition-all'
            ]"
          >
            {{ tab.name }}
          </button>
          <button
            @click="logout"
            class="ml-2 px-3 py-1.5 text-xs text-rose-600 hover:bg-rose-50 rounded-xl transition-all font-medium"
          >
            退出
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Login v-if="!token" @login-success="handleLoginSuccess" />
      <div v-else>
        <Dashboard v-if="activeTab === 'dashboard'" />
        <SourceManager v-if="activeTab === 'sources'" />
        <ImageGallery v-if="activeTab === 'gallery'" />
        <ApiKeyManager v-if="activeTab === 'keys'" />
      </div>
    </main>
  </div>
</template>

<script>
import Login from './components/Login.vue';
import Dashboard from './components/Dashboard.vue';
import SourceManager from './components/SourceManager.vue';
import ImageGallery from './components/ImageGallery.vue';
import ApiKeyManager from './components/ApiKeyManager.vue';

export default {
  name: 'App',
  components: {
    Login,
    Dashboard,
    SourceManager,
    ImageGallery,
    ApiKeyManager
  },
  data() {
    return {
      token: localStorage.getItem('token') || '',
      activeTab: 'dashboard',
      tabs: [
        { id: 'dashboard', name: '📊 概览看板' },
        { id: 'sources', name: '🗄️ AList 存储源' },
        { id: 'gallery', name: '🖼️ 图片画廊' },
        { id: 'keys', name: '🔑 API 密钥' }
      ]
    };
  },
  methods: {
    handleLoginSuccess(token) {
      this.token = token;
      localStorage.setItem('token', token);
      this.activeTab = 'dashboard';
    },
    logout() {
      localStorage.removeItem('token');
      this.token = '';
    }
  }
};
</script>
