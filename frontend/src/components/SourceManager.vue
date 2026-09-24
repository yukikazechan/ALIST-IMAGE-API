<template>
  <div class="space-y-6">
    <!-- Header & Action -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
      <div>
        <h2 class="text-xl font-bold text-slate-800">AList 存储源管理</h2>
        <p class="text-sm text-slate-500 mt-1">配置 AList 挂载目录，支持多层递归扫盘、自动提取目录标签与尺寸元数据</p>
      </div>
      <button
        @click="showAddModal = true"
        class="inline-flex items-center px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-xl shadow-sm transition-all duration-200 hover:shadow-indigo-100 hover:shadow-lg"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        添加 AList 存储源
      </button>
    </div>

    <!-- Sources Grid -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 3" :key="i" class="h-48 bg-slate-100 animate-pulse rounded-2xl"></div>
    </div>

    <div v-else-if="sources.length === 0" class="text-center py-16 bg-white rounded-2xl border border-dashed border-slate-200">
      <div class="w-16 h-16 bg-indigo-50 text-indigo-500 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h3 class="text-base font-semibold text-slate-700">暂无存储源</h3>
      <p class="text-sm text-slate-400 mt-1 max-w-sm mx-auto">添加您的首个 AList 服务器与目录，一键同步建立图片随机池</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="src in sources"
        :key="src.id"
        class="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between mb-3">
            <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold"
              :class="{
                'bg-emerald-50 text-emerald-600': src.sync_status === 'idle',
                'bg-amber-50 text-amber-600 animate-pulse': src.sync_status === 'syncing',
                'bg-rose-50 text-rose-600': src.sync_status === 'error'
              }"
            >
              <span class="w-1.5 h-1.5 rounded-full mr-1.5"
                :class="{
                  'bg-emerald-500': src.sync_status === 'idle',
                  'bg-amber-500': src.sync_status === 'syncing',
                  'bg-rose-500': src.sync_status === 'error'
                }"
              ></span>
              {{ src.sync_status === 'syncing' ? '正在同步...' : (src.sync_status === 'error' ? '同步失败' : '正常就绪') }}
            </span>
            <span class="text-xs text-slate-400">ID: {{ src.id }}</span>
          </div>

          <h3 class="text-lg font-bold text-slate-800 truncate mb-1">{{ src.name }}</h3>
          <p class="text-xs text-slate-400 font-mono truncate mb-4">{{ src.base_url }}{{ src.root_path }}</p>

          <div class="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-xl mb-4 text-center">
            <div>
              <div class="text-xs text-slate-400">索引图片</div>
              <div class="text-base font-bold text-slate-700">{{ src.total_images_indexed }}</div>
            </div>
            <div>
              <div class="text-xs text-slate-400">上次同步</div>
              <div class="text-xs font-medium text-slate-600 mt-1 truncate">{{ formatTime(src.last_sync_at) }}</div>
            </div>
          </div>

          <div v-if="src.sync_message" class="text-xs text-slate-500 bg-slate-50 p-2 rounded-lg truncate mb-4" :title="src.sync_message">
            {{ src.sync_message }}
          </div>
        </div>

        <button
          @click="handleSync(src.id)"
          :disabled="src.sync_status === 'syncing'"
          class="w-full inline-flex items-center justify-center px-4 py-2.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white text-sm font-medium rounded-xl transition-all"
        >
          <svg class="w-4 h-4 mr-2" :class="{'animate-spin': src.sync_status === 'syncing'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ src.sync_status === 'syncing' ? '正在扫盘同步...' : '立即增量同步' }}
        </button>
      </div>
    </div>

    <!-- Add Source Modal -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100">
        <h3 class="text-lg font-bold text-slate-800 mb-4">添加 AList 存储源</h3>
        <form @submit.prevent="submitAddSource" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">存储源名称</label>
            <input v-model="newSource.name" required placeholder="如：二次元 4K 壁纸库" class="w-full px-3.5 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">AList 根地址</label>
            <input v-model="newSource.base_url" required placeholder="http://127.0.0.1:5244" class="w-full px-3.5 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">挂载根目录</label>
            <input v-model="newSource.root_path" required placeholder="/Wallpapers/Anime" class="w-full px-3.5 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">API Token (可选)</label>
            <input v-model="newSource.token" type="password" placeholder="AList 管理令牌 (若目录需要密码/Token)" class="w-full px-3.5 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-500" />
          </div>
          <div class="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button type="button" @click="showAddModal = false" class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-xl font-medium">取消</button>
            <button type="submit" class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium shadow-sm">确认添加</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'SourceManager',
  data() {
    return {
      sources: [],
      loading: true,
      showAddModal: false,
      newSource: {
        name: '',
        base_url: 'http://127.0.0.1:5244',
        root_path: '/',
        token: ''
      }
    };
  },
  mounted() {
    this.fetchSources();
  },
  methods: {
    async fetchSources() {
      this.loading = true;
      try {
        const res = await api.getSources();
        this.sources = res.data;
      } catch (err) {
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async submitAddSource() {
      try {
        await api.createSource(this.newSource);
        this.showAddModal = false;
        this.newSource = { name: '', base_url: 'http://127.0.0.1:5244', root_path: '/', token: '' };
        await this.fetchSources();
      } catch (err) {
        alert('添加失败：' + (err.response?.data?.detail || err.message));
      }
    },
    async handleSync(id) {
      try {
        await api.syncSource(id);
        const item = this.sources.find(s => s.id === id);
        if (item) item.sync_status = 'syncing';
        setTimeout(() => this.fetchSources(), 2500);
      } catch (err) {
        alert('同步启动失败：' + err.message);
      }
    },
    formatTime(timeStr) {
      if (!timeStr) return '从未同步';
      const d = new Date(timeStr);
      return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  }
};
</script>
