<!--
  文件转换页面
  
  提供文件上传和格式转换功能
-->

<template>
  <div class="converter-container">
    <el-card class="converter-card">
      <template #header>
        <div class="card-header">
          <h2>文件格式转换</h2>
          <el-button type="primary" @click="goBack">返回首页</el-button>
        </div>
      </template>

      <el-steps :active="currentStep" finish-status="success" class="steps">
        <el-step title="选择文件" />
        <el-step title="选择格式" />
        <el-step title="开始转换" />
      </el-steps>

      <!-- 第一步：选择文件 -->
      <div v-show="currentStep === 0" class="step-content">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :on-change="handleFileChange"
          :file-list="fileList"
          drag
          multiple
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击选择</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持多种文件格式转换
            </div>
          </template>
        </el-upload>

        <div class="button-group">
          <el-button type="primary" :disabled="fileList.length === 0" @click="nextStep">
            下一步
          </el-button>
        </div>
      </div>

      <!-- 第二步：选择目标格式 -->
      <div v-show="currentStep === 1" class="step-content">
        <el-form label-width="100px">
          <el-form-item label="目标格式">
            <el-select v-model="targetFormat" placeholder="请选择目标格式">
              <el-option label="PDF" value="pdf" />
              <el-option label="Word (DOCX)" value="docx" />
              <el-option label="PowerPoint (PPTX)" value="pptx" />
              <el-option label="Excel (XLSX)" value="xlsx" />
              <el-option label="CSV" value="csv" />
              <el-option label="JSON" value="json" />
              <el-option label="PNG" value="png" />
              <el-option label="JPG" value="jpg" />
            </el-select>
          </el-form-item>
        </el-form>

        <div class="button-group">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" :disabled="!targetFormat" @click="nextStep">
            下一步
          </el-button>
        </div>
      </div>

      <!-- 第三步：开始转换 -->
      <div v-show="currentStep === 2" class="step-content">
        <div class="conversion-summary">
          <h3>转换信息确认</h3>
          <p>文件数量：{{ fileList.length }} 个</p>
          <p>目标格式：{{ targetFormat }}</p>
        </div>

        <el-progress
          v-if="converting"
          :percentage="progress"
          :status="progress === 100 ? 'success' : undefined"
        />

        <div class="button-group">
          <el-button @click="prevStep" :disabled="converting">上一步</el-button>
          <el-button type="primary" @click="startConversion" :loading="converting">
            {{ converting ? '转换中...' : '开始转换' }}
          </el-button>
        </div>

        <!-- 转换结果 -->
        <div v-if="conversionResults.length > 0" class="results">
          <h3>转换结果</h3>
          <el-table :data="conversionResults" border>
            <el-table-column prop="fileName" label="文件名" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.success ? 'success' : 'danger'">
                  {{ row.success ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button
                  v-if="row.success"
                  size="small"
                  type="primary"
                  @click="downloadFile(row)"
                >
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { fileAPI } from '@/api/file'
import type { UploadFile } from 'element-plus'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 文件列表
const fileList = ref<UploadFile[]>([])

// 目标格式
const targetFormat = ref('')

// 转换状态
const converting = ref(false)
const progress = ref(0)

// 转换结果
const conversionResults = ref<Array<{
  fileName: string
  success: boolean
  downloadUrl?: string
}>>([])

// 处理文件变化
const handleFileChange = (file: UploadFile, files: UploadFile[]) => {
  fileList.value = files
}

// 下一步
const nextStep = () => {
  if (currentStep.value < 2) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 开始转换
const startConversion = async () => {
  converting.value = true
  progress.value = 0
  conversionResults.value = []

  try {
    // 模拟进度
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 10
      }
    }, 200)

    // 批量转换文件
    const files = fileList.value.map(f => f.raw as File)
    const result = await fileAPI.batchConvert(
      files,
      targetFormat.value,
      (p) => {
        progress.value = p
      }
    )

    clearInterval(progressInterval)
    progress.value = 100

    // 处理结果
    result.results.forEach(r => {
      conversionResults.value.push({
        fileName: r.file,
        success: r.result.success,
        downloadUrl: r.result.download_url
      })
    })

    ElMessage.success(
      `转换完成！成功 ${result.success_count} 个，失败 ${result.failed_count} 个`
    )
  } catch (error: any) {
    ElMessage.error(error.message || '转换失败')
  } finally {
    converting.value = false
  }
}

// 下载文件
const downloadFile = async (row: any) => {
  try {
    if (row.downloadUrl) {
      await fileAPI.downloadFile(row.downloadUrl, row.fileName)
      ElMessage.success('下载成功')
    }
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 返回首页
const goBack = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.converter-container {
  min-height: 100vh;
  background-color: #f0f2f5;
  padding: 30px;
}

.converter-card {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
}

.steps {
  margin: 30px 0;
}

.step-content {
  margin-top: 30px;
  min-height: 300px;
}

.button-group {
  margin-top: 30px;
  text-align: center;
}

.button-group .el-button {
  margin: 0 10px;
}

.conversion-summary {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.conversion-summary h3 {
  margin: 0 0 15px 0;
}

.conversion-summary p {
  margin: 10px 0;
  font-size: 16px;
}

.results {
  margin-top: 30px;
}

.results h3 {
  margin: 0 0 15px 0;
}
</style>
