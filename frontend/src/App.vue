<template>
  <div v-if="!isAuthenticated">
    <Login @authenticated="handleAuthentication" />
  </div>
  <div v-else class="app-container">
    <header class="app-header">
      <h1>Alist Image API</h1>
      <el-button @click="handleLogout" class="logout-button">Logout</el-button>
    </header>
    <main class="app-main">
      <el-tabs v-model="activeTab" class="main-tabs">
        <el-tab-pane label="Image Gallery" name="gallery">
          <image-uploader :all-tags="allTags" @tags-updated="handleTagsUpdate" />
          <el-divider />
          <image-gallery :key="galleryKey" :all-tags="allTags" @tags-updated="handleTagsUpdate" />
        </el-tab-pane>
        <el-tab-pane label="API Key Management" name="api-keys">
          <api-key-manager :all-tags="allTags" @tags-updated="handleTagsUpdate" />
        </el-tab-pane>
        <el-tab-pane v-if="currentUser && currentUser.is_admin" label="User Management" name="user-management">
          <user-management />
        </el-tab-pane>
        <el-tab-pane label="My Profile" name="my-profile">
          <user-profile />
        </el-tab-pane>
        <el-tab-pane label="API Usage" name="api-usage">
          <el-card class="usage-card">
            <h2>How to use the API</h2>
            <p>You can get a random image by using the following API endpoint format. The API will act as a proxy and directly return the image, which can be used in `<img>` tags.</p>
            <h4>API Endpoint</h4>
            <code>{{ apiUrlBase }}/api/v1/random/YOUR_API_KEY</code>
            <p>Replace <code>YOUR_API_KEY</code> with a key you generated in the "API Key Management" tab.</p>
            <p>The behavior of the endpoint (which tags to use and whether to match ALL or ANY of them) is defined when you create the API Key.</p>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import ImageUploader from './components/ImageUploader.vue';
import ImageGallery from './components/ImageGallery.vue';
import ApiKeyManager from './components/ApiKeyManager.vue';
import Login from './components/Login.vue';
import UserManagement from './components/UserManagement.vue';
import UserProfile from './components/UserProfile.vue';
import { getImages, getCurrentUser } from './services/api';

const activeTab = ref('gallery');
const allTags = ref([]);
const isAuthenticated = ref(false);
const currentUser = ref(null);
const galleryKey = ref(0);
const apiUrlBase = computed(() => window.location.origin);

const fetchCurrentUser = async () => {
  try {
    currentUser.value = await getCurrentUser();
  } catch (error) {
    console.error("Failed to fetch current user", error);
    // This might happen if the token is invalid, so log out.
    handleLogout();
  }
};

const checkAuth = () => {
  const token = localStorage.getItem('token');
  if (token) {
    isAuthenticated.value = true;
    fetchAllTags();
    fetchCurrentUser();
  }
};

const handleAuthentication = () => {
  isAuthenticated.value = true;
  fetchAllTags();
  fetchCurrentUser();
};

const handleLogout = () => {
  localStorage.removeItem('token');
  isAuthenticated.value = false;
  currentUser.value = null;
  // Force a reload to ensure a clean state for the entire application
  window.location.reload();
};

const fetchAllTags = async () => {
  try {
    const data = await getImages({ limit: 1000 }); // A simple way to get all tags
    const tagSet = new Set();
    data.images.forEach(image => {
      image.tags.forEach(tag => tagSet.add(tag.name));
    });
    allTags.value = Array.from(tagSet).sort();
  } catch (error) {
    console.error('Failed to fetch all tags:', error);
  }
};

const handleTagsUpdate = () => {
  fetchAllTags();
  galleryKey.value++;
};

onMounted(() => {
  checkAuth();
});
</script>

<style>
/* Global Styles */
body {
  background-color: #f4f7f9;
  color: #1f2937;
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', "\\\\5FAE软雅黑", Arial, sans-serif;
}

.app-container {
  padding: 0 2rem;
}

/* Header */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 2rem;
  text-align: center;
  margin: 0 -2rem; /* Extend to full width */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logout-button {
  position: absolute;
  right: 2rem;
}

.app-header h1 {
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.app-main {
  padding: 2rem 0;
}

/* Tabs */
.main-tabs .el-tabs__header {
  margin-bottom: 2rem;
}
.main-tabs .el-tabs__item {
  font-size: 1rem;
  color: #6b7280;
  padding: 0 20px;
}
.main-tabs .el-tabs__item.is-active {
  color: #3B82F6;
}
.main-tabs .el-tabs__active-bar {
  background-color: #3B82F6;
  height: 3px;
}
.main-tabs .el-tabs__nav-wrap::after {
  display: none; /* Remove default bottom border */
}

/* General Card Style */
.el-card {
  border-radius: 12px !important;
  border: none !important;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) !important;
}

.usage-card {
  padding: 1.5rem;
}
.usage-card h2 {
  margin-top: 0;
  color: #1f2937;
}
.usage-card code {
  background-color: #e9e9eb;
  padding: 3px 6px;
  border-radius: 6px;
  margin: 0 4px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
}
</style>