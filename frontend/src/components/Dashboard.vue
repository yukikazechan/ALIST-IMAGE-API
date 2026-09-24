<template>
  <div class="space-y-6">
    <!-- Stat Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">图片库总数</div>
          <div class="text-2xl font-bold text-slate-800 mt-0.5">{{ stats.total_images }}</div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div>
          <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">AList 存储源</div>
          <div class="text-2xl font-bold text-slate-800 mt-0.5">{{ stats.total_sources }}</div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-violet-50 text-violet-600 flex items-center justify-center">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
        </div>
        <div>
          <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">活跃 API 密钥</div>
          <div class="text-2xl font-bold text-slate-800 mt-0.5">{{ stats.total_api_keys }}</div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">全网总调用量</div>
          <div class="text-2xl font-bold text-slate-800 mt-0.5">{{ stats.total_calls_all_time }}</div>
        </div>
      </div>
    </div>

    <!-- Top Tags & Quick Guide -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm lg:col-span-1">
        <h3 class="text-base font-bold text-slate-800 mb-4">热门标签分布 (Top 10)</h3>
        <div v-if="stats.top_tags.length === 0" class="text-sm text-slate-400 py-6 text-center">暂无标签统计</div>
        <div v-else class="space-y-3">
          <div v-for="tag in stats.top_tags" :key="tag.name" class="flex items-center justify-between text-sm">
            <span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-medium text-xs">
              # {{ tag.name }}
            </span>
            <span class="font-bold text-slate-600">{{ tag.count }} 张</span>
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm lg:col-span-2 flex flex-col justify-between">
        <div>
          <h3 class="text-base font-bold text-slate-800 mb-2">⚡ 快速调用指南 (API Quickstart)</h3>
          <p class="text-sm text-slate-500 mb-4">通过任意 API 密钥直接在网页、博客或 Markdown 中嵌入随机图：</p>
          
          <div class="space-y-3">
            <div class="bg-slate-900 rounded-xl p-4 text-xs font-mono text-emerald-400 overflow-x-auto">
              # 1. 网页直接插入 302 重定向图片（最省带宽）<br>
              &lt;img src="http://your-server:5235/api/v1/random/YOUR_KEY" /&gt;
            </div>
            <div class="bg-slate-900 rounded-xl p-4 text-xs font-mono text-cyan-300 overflow-x-auto">
              # 2. 动态 WebP 压缩代理模式<br>
              GET /api/v1/random/YOUR_KEY?format=proxy&webp=true&orientation=landscape
            </div>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
          <span>ALIST-IMAGE-API v2.0 · 零 DB 开销极速引擎</span>
          <span class="text-emerald-500 font-medium flex items-center">
            <span class="w-2 h-2 rounded-full bg-emerald-500 mr-1.5"></span>内存随机池就绪
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        total_images: 0,
        total_sources: 0,
        total_tags: 0,
        total_api_keys: 0,
        total_calls_all_time: 0,
        top_tags: []
      }
    };
  },
  mounted() {
    this.fetchStats();
  },
  methods: {
    async fetchStats() {
      try {
        const res = await api.getDashboardStats();
        this.stats = res.data;
      } catch (err) {
        console.error(err);
      }
    }
  }
};
</script>
