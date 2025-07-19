<template>
  <div>
    <el-form :model="form" inline>
      <el-form-item label="Key Name">
        <el-input v-model="form.name" placeholder="Enter a name for the key"></el-input>
      </el-form-item>
      <el-form-item label="Tags (AND)">
        <el-select
          v-model="form.tags_and"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="Tags that must all be present"
          style="width: 220px"
        >
          <el-option v-for="tag in allTags" :key="tag" :label="tag" :value="tag" />
        </el-select>
      </el-form-item>
      <el-form-item label="Tags (OR)">
        <el-select
          v-model="form.tags_or"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="Tags where at least one is present"
          style="width: 220px"
        >
          <el-option v-for="tag in allTags" :key="tag" :label="tag" :value="tag" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleCreateKey">Create API Key</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="apiKeys" style="width: 100%">
      <el-table-column prop="name" label="Name" />
      <el-table-column prop="key" label="API Key">
        <template #default="{ row }">
          <code>{{ row.key }}</code>
          <el-button link type="primary" @click="copyToClipboard(row.key)">Copy</el-button>
        </template>
      </el-table-column>
      <el-table-column label="Tags (AND)">
        <template #default="{ row }">
          <el-tag v-for="tag in row.tags_and" :key="tag.id" type="success" style="margin-right: 5px;">{{ tag.name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Tags (OR)">
        <template #default="{ row }">
          <el-tag v-for="tag in row.tags_or" :key="tag.id" type="info" style="margin-right: 5px;">{{ tag.name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="API URL">
        <template #default="{ row }">
          <el-button link type="primary" @click="copyToClipboard(`http://localhost:8000/api/v1/random/${row.key}`)">Copy URL</el-button>
        </template>
      </el-table-column>
      <el-table-column label="Actions">
        <template #default="{ row }">
          <el-button type="danger" size="small" @click="handleDeleteKey(row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, defineProps, defineEmits } from 'vue';
import { getApiKeys, addApiKey, deleteApiKey } from '../services/api';
import { ElMessage } from 'element-plus';

const props = defineProps({
  allTags: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['tags-updated']);

const apiKeys = ref([]);
const form = reactive({
  name: '',
  tags_and: [],
  tags_or: [],
});

const fetchApiKeys = async () => {
  try {
    apiKeys.value = await getApiKeys();
    // Initialize selectedTags for each key
  } catch (error) {
    console.error('Failed to fetch API keys:', error);
    ElMessage.error('Failed to fetch API keys.');
  }
};

const handleCreateKey = async () => {
  if (!form.name) {
    ElMessage.error('Key name is required.');
    return;
  }
  try {
    await addApiKey({ name: form.name, tags_and: form.tags_and, tags_or: form.tags_or });
    ElMessage.success('API Key created successfully!');
    form.name = '';
    form.tags_and = [];
    form.tags_or = [];
    fetchApiKeys();
    emit('tags-updated'); // Notify parent
  } catch (error) {
    console.error('Failed to create API key:', error);
    ElMessage.error('Failed to create API key.');
  }
};

const handleDeleteKey = async (id) => {
  try {
    await deleteApiKey(id);
    apiKeys.value = apiKeys.value.filter(key => key.id !== id);
    ElMessage.success('API Key deleted successfully!');
  } catch (error) {
    console.error('Failed to delete API key:', error);
    ElMessage.error('Failed to delete API key.');
  }
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('Copied to clipboard!');
  }, () => {
    ElMessage.error('Failed to copy!');
  });
};

onMounted(() => {
  fetchApiKeys();
});
</script>