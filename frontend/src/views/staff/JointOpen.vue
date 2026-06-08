<template>
  <div>
    <PageHeader title="联合开户" />

    <PagePanel width="narrow">
      <PageInfoCard title="办理说明" style="margin-bottom: 24px;">
        <p class="inline-tip">
          本页仅提交联合开户申请。审批通过时由审批人员设置银行卡号、交易密码和取款密码，
          系统随后连续创建证券账户、资金账户并建立一对一有效绑定。
        </p>
      </PageInfoCard>

      <PageFormBlock>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="page-form-stack"
          @submit.prevent
        >
          <el-form-item label="投资者姓名" label-position="top" prop="investorName" style="margin-bottom: 0;">
            <el-input v-model="form.investorName" placeholder="请输入姓名" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="证件类型" label-position="top" prop="idType" style="margin-bottom: 0;">
            <el-select v-model="form.idType" placeholder="请选择" style="width: 100%;">
              <el-option
                v-for="(label, key) in IdTypeLabel"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="证件号码" label-position="top" prop="idNo" style="margin-bottom: 0;">
            <el-input v-model="form.idNo" placeholder="请输入证件号码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="联系电话" label-position="top" prop="phone" style="margin-bottom: 0;">
            <el-input v-model="form.phone" placeholder="请输入手机号" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="申请备注" label-position="top" prop="remark" style="margin-bottom: 0;">
            <el-input
              v-model="form.remark"
              type="textarea"
              :rows="3"
              maxlength="1000"
              show-word-limit
              placeholder="可填写开户申请备注"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>

        <PageActionRow
          primary-text="提交联合开户申请"
          secondary-text="重置"
          :primary-disabled="loading"
          @primary="submitJoint"
          @secondary="resetForm"
        />
      </PageFormBlock>
    </PagePanel>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { submitOpenApplication } from '@/utils/request'
import { IdTypeLabel } from '@/constants/enums'
import PageActionRow from '@/components/PageActionRow.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageInfoCard from '@/components/PageInfoCard.vue'
import PagePanel from '@/components/PagePanel.vue'

const buildInitialForm = () => ({
  investorName: '',
  idType: 'ID_CARD',
  idNo: '',
  phone: '',
  remark: '联合开户申请'
})

const form = reactive(buildInitialForm())
const formRef = ref(null)
const loading = ref(false)

const rules = {
  investorName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  idType: [{ required: true, message: '请选择证件类型', trigger: 'change' }],
  idNo: [{ required: true, message: '请输入证件号码', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const submitJoint = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await submitOpenApplication({
      investorName: form.investorName.trim(),
      idType: form.idType,
      idNo: form.idNo.trim(),
      phone: form.phone.trim(),
      remark: form.remark.trim() || '联合开户申请'
    })
    ElMessage.success(`联合开户申请已提交，申请编号：${res.data.applicationId}`)
    resetForm()
  } catch (error) {
    ElMessage.error(error.message || '开户申请提交失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.assign(form, buildInitialForm())
  formRef.value?.resetFields()
}
</script>

<style scoped>
.page-form-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.inline-tip {
  margin: 0;
  line-height: 1.7;
  color: var(--color-text-muted);
}
</style>
