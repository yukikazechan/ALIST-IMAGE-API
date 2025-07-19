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
      <el-table-column label="API Endpoint URL">
        <template #default="{ row }">
          <el-button link type="primary" @click="copyToClipboard(`${apiEndpoint}/api/v1/random/${row.key}`)">Copy</el-button>
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
import { getApiKeys, addApiKey, deleteApiKey, getAppConfig } from '../services/api';
import { ElMessage } from 'element-plus';

const apiEndpoint = ref('');

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
  console.log('Attempting to copy:', text);
  // Use modern clipboard API in secure contexts
  if (navigator.clipboard && window.isSecureContext) {
    console.log('Using navigator.clipboard API.');
    navigator.clipboard.writeText(text).then(() => {
      console.log('Copy successful with navigator.clipboard');
      ElMessage.success('Copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy with navigator.clipboard:', err);
      ElMessage.error('Failed to copy! See console for details.');
    });
  } else {
    // Fallback for older browsers or insecure contexts (HTTP)
    console.log('Using fallback execCommand for insecure context or older browser.');
    const textArea = document.createElement('textarea');
    textArea.value = text;
    
    // Make the textarea non-editable and move it off-screen
    textArea.style.position = 'absolute';
    textArea.style.left = '-9999px';
    textArea.setAttribute('readonly', '');

    document.body.appendChild(textArea);
    console.log('Fallback textarea appended to body.');
    
    textArea.select();
    // For mobile devices
    textArea.setSelectionRange(0, 99999);

    try {
      const successful = document.execCommand('copy');
      console.log('document.execCommand successful:', successful);
      if (successful) {
        ElMessage.success('Copied to clipboard!');
      } else {
        ElMessage.error('Fallback copy failed: execCommand returned false.');
        console.error('Fallback copy failed: execCommand returned false.');
      }
    } catch (err) {
      console.error('Fallback copy failed with error:', err);
      ElMessage.error('Fallback copy failed! See console for details.');
    }

    document.body.removeChild(textArea);
    console.log('Fallback textarea removed from body.');
  }
};

onMounted(async () => {
  fetchApiKeys();
  try {
    const config = await getAppConfig();
    apiEndpoint.value = config.api_endpoint;
    console.log('Fetched API endpoint:', apiEndpoint.value);
  } catch (error) {
    console.error('Failed to fetch app config:', error);
    ElMessage.error('Could not load API endpoint configuration.');
  }
});
</script>