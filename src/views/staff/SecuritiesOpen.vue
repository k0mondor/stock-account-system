<!-- src/views/staff/SecuritiesOpen.vue -->
<template>
  <div>
    <PageHeader title="开设证券账户" />

    <el-card style="margin: 24px auto 0; max-width: 720px; background: var(--color-white);">
      <!-- 步骤条 -->
      <el-steps :active="activeStep" finish-status="success" align-center style="margin-bottom: 32px;">
        <el-step title="信息录入" description="填写投资者基本信息" />
        <el-step title="合规审查" description="设置账户密码" />
        <el-step title="开户成功" description="完成开户流程" />
      </el-steps>

      <!-- 步骤1：信息录入 -->
      <div v-show="activeStep === 0">
         <h3 style="text-align: center; margin-bottom: 24px; color: #333;">请选择账户类型</h3>
         <div style="display: flex; justify-content: center; gap: 24px; margin-bottom: 32px;">
           <el-button 
             :type="accountType === 'PERSONAL' ? 'primary' : 'default'"
             @click="accountType = 'PERSONAL'"
             style="padding: 10px 28px; font-size: 14px; font-weight: 500; border-radius: 0;"
           >
             个人账户
           </el-button>
           <el-button 
             :type="accountType === 'CORPORATE' ? 'primary' : 'default'"
             @click="accountType = 'CORPORATE'"
             style="padding: 10px 28px; font-size: 14px; font-weight: 500; border-radius: 0;"
           >
             法人账户
           </el-button>
         </div>

        <el-form 
          ref="formRef" 
          :model="formData" 
          :rules="currentRules" 
          @submit.prevent 
          style="display: flex; flex-direction: column; gap: 20px;"
        >
          <!-- 个人账户表单 -->
          <div v-if="accountType === 'PERSONAL'">
            <el-form-item label="客户姓名" label-position="top" prop="clientName" style="margin-bottom: 0;">
              <el-input v-model="formData.clientName" placeholder="请输入客户姓名" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="本人性别" label-position="top" prop="gender" style="margin-bottom: 0;">
              <el-radio-group v-model="formData.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="身份证号码" label-position="top" prop="idCardNo" style="margin-bottom: 0;">
              <el-input v-model="formData.idCardNo" placeholder="请输入18位身份证号码" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="家庭地址" label-position="top" prop="address" style="margin-bottom: 0;">
              <el-input v-model="formData.address" type="textarea" placeholder="请输入家庭地址" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="联系电话" label-position="top" prop="phone" style="margin-bottom: 0;">
              <el-input v-model="formData.phone" placeholder="请输入手机号码" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="本人职业" label-position="top" prop="profession" style="margin-bottom: 0;">
              <el-select v-model="formData.profession" placeholder="请选择职业" style="width: 100%;">
                <el-option label="职员" value="employee" />
                <el-option label="自由职业" value="freelancer" />
                <el-option label="技术人员" value="technician" />
                <el-option label="管理人员" value="manager" />
                <el-option label="学生" value="student" />
                <el-option label="退休人员" value="retiree" />
                <el-option label="证券从业人员" value="securities_employee" />
              </el-select>
            </el-form-item>

            <el-form-item label="本人学历" label-position="top" prop="education" style="margin-bottom: 0;">
              <el-select v-model="formData.education" placeholder="请选择学历" style="width: 100%;">
                <el-option label="高中及以下" value="high_school_or_below" />
                <el-option label="大专" value="associate_degree" />
                <el-option label="本科" value="bachelor_degree" />
                <el-option label="硕士" value="master_degree" />
                <el-option label="博士" value="doctoral_degree" />
              </el-select>
            </el-form-item>

            <el-form-item label="工作单位" label-position="top" style="margin-bottom: 0;">
              <el-input v-model="formData.company" placeholder="请输入工作单位" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="是否代办" label-position="top" style="margin-bottom: 0;">
              <el-radio-group v-model="formData.isAgent">
                <el-radio label="本人办理">本人办理</el-radio>
                <el-radio label="他人代办">他人代办</el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 代办人信息（条件显示） -->
            <div v-if="formData.isAgent === '他人代办'">
              <el-form-item label="代办人姓名" label-position="top" prop="proxyName" style="margin-bottom: 0;">
                <el-input v-model="formData.proxyName" placeholder="请输入代办人姓名" style="width: 100%;" />
              </el-form-item>

              <el-form-item label="代办人身份证号" label-position="top" prop="proxyIdCardNo" style="margin-bottom: 0;">
                <el-input v-model="formData.proxyIdCardNo" placeholder="请输入代办人身份证号码" style="width: 100%;" />
              </el-form-item>
            </div>
          </div>

          <!-- 法人账户表单 -->
          <div v-else-if="accountType === 'CORPORATE'">
            <el-form-item label="企业名称" label-position="top" prop="corporateName" style="margin-bottom: 0;">
              <el-input v-model="formData.corporateName" placeholder="请输入企业名称" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="营业执照号码" label-position="top" prop="businessLicenseNo" style="margin-bottom: 0;">
              <el-input v-model="formData.businessLicenseNo" placeholder="请输入营业执照号码" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="有效的法人注册登记号码" label-position="top" prop="registrationNo" style="margin-bottom: 0;">
              <el-input v-model="formData.registrationNo" placeholder="请输入法人注册登记号码" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="法定代表人姓名" label-position="top" prop="legalPersonName" style="margin-bottom: 0;">
              <el-input v-model="formData.legalPersonName" placeholder="请输入法定代表人姓名" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="法定代表人身份证号" label-position="top" prop="legalPersonIdNo" style="margin-bottom: 0;">
              <el-input v-model="formData.legalPersonIdNo" placeholder="请输入法定代表人身份证号码" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="法人联系电话" label-position="top" prop="legalPhone" style="margin-bottom: 0;">
              <el-input v-model="formData.legalPhone" placeholder="请输入法人联系电话" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="法人联系地址" label-position="top" prop="legalAddress" style="margin-bottom: 0;">
              <el-input v-model="formData.legalAddress" type="textarea" placeholder="请输入法人联系地址" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="法定代表人授权证券交易执行人姓名" label-position="top" prop="agentName" style="margin-bottom: 0;">
              <el-input v-model="formData.agentName" placeholder="请输入授权人姓名" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="授权人有效身份证号码" label-position="top" prop="agentIdNo" style="margin-bottom: 0;">
              <el-input v-model="formData.agentIdNo" placeholder="请输入授权人身份证号码" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="授权人联系电话" label-position="top" prop="agentPhone" style="margin-bottom: 0;">
              <el-input v-model="formData.agentPhone" placeholder="请输入授权人联系电话" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="授权人地址" label-position="top" prop="agentAddress" style="margin-bottom: 0;">
              <el-input v-model="formData.agentAddress" placeholder="请输入授权人地址" style="width: 100%;" />
            </el-form-item>
          </div>
        </el-form>

        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <el-button 
            type="primary" 
            @click="nextStep" 
            :disabled="!accountType"
            style="padding: 10px 28px; font-size: 14px; font-weight: 500; border-radius: 0;"
          >
            下一步
          </el-button>
          <el-button 
            class="btn-secondary" 
            style="margin-left: 12px; border-radius: 0;" 
            @click="resetForm"
          >
            重置
          </el-button>
        </div>
      </div>

      <!-- 步骤2：合规审查与密码设置 -->
      <div v-show="activeStep === 1">
        <h3 style="text-align: center; margin-bottom: 24px; color: #333;">合规审查与密码设置</h3>
        
        <div style="text-align: center; margin-bottom: 24px;">
          <el-alert
            title="正在审核您的申请，请稍候..."
            type="info"
            :closable="false"
            show-icon
          />
        </div>

        <!-- 合规审查结果 -->
        <div v-if="complianceCheckResult" style="margin-bottom: 24px;">
          <el-alert
            :title="complianceCheckResult.title"
            :type="complianceCheckResult.type"
            :closable="false"
            show-icon
          />
        </div>

        <!-- 密码设置按钮 -->
        <div style="text-align: center; margin-top: 32px;" v-if="compliancePassed">
          <el-button 
            type="primary" 
            @click="showPasswordDialog = true"
            style="padding: 12px 32px; font-size: 16px; border-radius: 0;"
          >
            设置账户密码
          </el-button>
          <p style="margin-top: 12px; color: #666; font-size: 14px;">
            请指引客户在密码键盘上设置交易密码和取款密码
          </p>
        </div>

        <!-- 上一步/下一步按钮 -->
        <div style="display: flex; justify-content: center; margin-top: 32px;">
          <el-button 
            class="btn-secondary" 
            @click="prevStep"
            style="border-radius: 0;"
          >
            上一步
          </el-button>
          <el-button 
            type="primary" 
            @click="nextStep"
            :disabled="!compliancePassed || !hasSetPasswords"
            style="margin-left: 12px; border-radius: 0;"
          >
            确认开户
          </el-button>
        </div>
      </div>

      <!-- 步骤3：开户成功 -->
      <div v-show="activeStep === 2">
        <div style="text-align: center; padding: 40px 0;">
          <el-result icon="success" title="开户成功！" sub-title="恭喜您，证券账户已成功开立">
            <template #extra>
              <div>
                <p style="font-size: 16px; font-weight: bold; margin-bottom: 16px;">
                  证券账户号：{{ newAccountNo }}
                </p>
                <p style="color: #666; margin-bottom: 24px;">
                  请妥善保管您的账户信息和密码
                </p>
                <el-button 
                  type="primary" 
                  @click="printVoucher"
                  style="margin-right: 12px; border-radius: 0;"
                >
                  打印开户凭证
                </el-button>
                <el-button 
                  class="btn-secondary"
                  @click="finishProcess"
                  style="border-radius: 0;"
                >
                  完成
                </el-button>
              </div>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>

    <!-- 密码设置弹窗 -->
    <el-dialog v-model="showPasswordDialog" title="设置账户密码" width="400px" :close-on-click-modal="false" :close-on-press-escape="false">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
        <el-form-item label="交易密码" prop="tradePassword">
          <el-input v-model="passwordForm.tradePassword" type="password" show-password placeholder="请输入交易密码" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="取款密码" prop="withdrawPassword">
          <el-input v-model="passwordForm.withdrawPassword" type="password" show-password placeholder="请输入取款密码" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer" style="display: flex; justify-content: flex-end; gap: 12px;">
          <el-button @click="cancelPasswordSetting">取消</el-button>
          <el-button type="primary" @click="confirmPasswordSetting">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { openSecuritiesAccount } from '@/utils/request'
import { IdTypeLabel } from '@/constants/enums'
import PageHeader from '@/components/PageHeader.vue'

// 当前步骤
const activeStep = ref(0)
const accountType = ref('PERSONAL')

// 表单数据
const formData = ref({
  // 个人账户字段
  clientName: '',
  gender: '',
  idCardNo: '',
  address: '',
  phone: '',
  profession: '',
  education: '',
  company: '',
  isAgent: '本人办理',
  proxyName: '',
  proxyIdCardNo: '',
  // 法人账户字段
  corporateName: '',
  businessLicenseNo: '',
  registrationNo: '',
  legalPersonName: '',
  legalPersonIdNo: '',
  legalPhone: '',
  legalAddress: '',
  agentName: '',
  agentIdNo: '',
  agentPhone: '',
  agentAddress: ''
})

const formRef = ref(null)

// 密码相关
const showPasswordDialog = ref(false)
const hasSetPasswords = ref(false)
const passwordForm = ref({
  tradePassword: '',
  withdrawPassword: ''
})
const passwordFormRef = ref(null)
const passwordRules = {
  tradePassword: [
    { required: true, message: '请输入交易密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度应在8-20位之间', trigger: 'blur' },
    { pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ],
  withdrawPassword: [
    { required: true, message: '请输入取款密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度应在8-20位之间', trigger: 'blur' },
    { pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]/, message: '密码必须包含字母和数字', trigger: 'blur' }
  ]
}

// 合规审查结果
const complianceCheckResult = ref(null)
const compliancePassed = ref(false)

// 新生成的账户号
const newAccountNo = ref('')

// 正则表达式
const idCardRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
const phoneRegex = /^1[3-9]\d{9}$/

// 个人账户验证规则
const personalRules = {
  clientName: [{ required: true, message: '请输入客户姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  idCardNo: [
    { required: true, message: '请输入身份证号码', trigger: 'blur' },
    { pattern: idCardRegex, message: '请输入正确的身份证号码', trigger: 'blur' }
  ],
  address: [{ required: true, message: '请输入家庭地址', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: phoneRegex, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  profession: [{ required: true, message: '请选择职业', trigger: 'change' }],
  education: [{ required: true, message: '请选择学历', trigger: 'change' }],
  proxyName: [
    { required: true, message: '请输入代办人姓名', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (formData.value.isAgent === '他人代办' && !value) {
        callback(new Error('请输入代办人姓名'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  proxyIdCardNo: [
    { required: true, message: '请输入代办人身份证号', trigger: 'blur' },
    { pattern: idCardRegex, message: '请输入正确的身份证号码', trigger: 'blur' }
  ]
}

// 法人账户验证规则
const corporateRules = {
  corporateName: [{ required: true, message: '请输入企业名称', trigger: 'blur' }],
  businessLicenseNo: [{ required: true, message: '请输入营业执照号码', trigger: 'blur' }],
  registrationNo: [{ required: true, message: '请输入法人注册登记号码', trigger: 'blur' }],
  legalPersonName: [{ required: true, message: '请输入法定代表人姓名', trigger: 'blur' }],
  legalPersonIdNo: [
    { required: true, message: '请输入法定代表人身份证号', trigger: 'blur' },
    { pattern: idCardRegex, message: '请输入正确的身份证号码', trigger: 'blur' }
  ],
  legalPhone: [
    { required: true, message: '请输入法人联系电话', trigger: 'blur' },
    { pattern: phoneRegex, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  legalAddress: [{ required: true, message: '请输入法人联系地址', trigger: 'blur' }],
  agentName: [{ required: true, message: '请输入授权人姓名', trigger: 'blur' }],
  agentIdNo: [
    { required: true, message: '请输入授权人身份证号', trigger: 'blur' },
    { pattern: idCardRegex, message: '请输入正确的身份证号码', trigger: 'blur' }
  ],
  agentPhone: [
    { required: true, message: '请输入授权人联系电话', trigger: 'blur' },
    { pattern: phoneRegex, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  agentAddress: [{ required: true, message: '请输入授权人地址', trigger: 'blur' }]
}

// 当前验证规则
const currentRules = computed(() => {
  return accountType.value === 'PERSONAL' ? personalRules : corporateRules
})

// 计算年龄（基于身份证号）
const calculateAge = (idCard) => {
  if (!idCard) return 0
  const birthYear = parseInt(idCard.substring(6, 10))
  const currentYear = new Date().getFullYear()
  return currentYear - birthYear
}

// 合规检查
const performComplianceCheck = () => {
  try {
    if (accountType.value === 'PERSONAL') {
      // 检查身份证号
      if (!idCardRegex.test(formData.value.idCardNo)) {
        complianceCheckResult.value = {
          title: '身份证号码格式不正确',
          type: 'error'
        }
        compliancePassed.value = false
        return
      }

      // 检查年龄（是否未成年人）
      const age = calculateAge(formData.value.idCardNo)
      if (age < 18) {
        complianceCheckResult.value = {
          title: '未成年人（未满18岁）不能单独开户',
          type: 'error'
        }
        compliancePassed.value = false
        return
      }

      // 检查职业（是否证券从业人员）
      if (formData.value.profession === 'securities_employee') {
        complianceCheckResult.value = {
          title: '证券从业人员禁止开户',
          type: 'error'
        }
        compliancePassed.value = false
        return
      }
    }

    // 如果都通过了检查
    complianceCheckResult.value = {
      title: '合规审查通过',
      type: 'success'
    }
    compliancePassed.value = true
  } catch (error) {
    complianceCheckResult.value = {
      title: '合规审查失败，请检查输入信息',
      type: 'error'
    }
    compliancePassed.value = false
  }
}

// 下一步
const nextStep = async () => {
  if (activeStep.value === 0) {
    // 验证当前表单
    try {
      await formRef.value.validate()
      activeStep.value = 1
      // 执行合规检查
      performComplianceCheck()
    } catch (error) {
      ElMessage.error('请完善必填信息')
    }
  } else if (activeStep.value === 1) {
    if (compliancePassed.value && hasSetPasswords.value) {
      // 执行开户
      handleOpen()
    } else {
      ElMessage.error('请先完成合规审查和密码设置')
    }
  } else if (activeStep.value === 2) {
    finishProcess()
  }
}

// 上一步
const prevStep = () => {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

// 确认密码设置
const confirmPasswordSetting = async () => {
  try {
    await passwordFormRef.value.validate()
    hasSetPasswords.value = true
    showPasswordDialog.value = false
    ElMessage.success('密码设置成功')
  } catch (error) {
    ElMessage.error('请完善密码信息')
  }
}

// 取消密码设置
const cancelPasswordSetting = () => {
  showPasswordDialog.value = false
  passwordForm.value = { tradePassword: '', withdrawPassword: '' }
  hasSetPasswords.value = false
}

// 开户处理
const handleOpen = async () => {
  try {
    const submitData = {
      ...formData.value,
      accountType: accountType.value,
      tradePassword: passwordForm.value.tradePassword,
      withdrawPassword: passwordForm.value.withdrawPassword
    }
    
    const res = await openSecuritiesAccount(submitData)
    newAccountNo.value = res.data.accountNo
    activeStep.value = 2
    ElMessage.success(`开户成功！证券账户号：${res.data.accountNo}`)
  } catch (e) {
    ElMessage.error(e.message || '开户失败')
  }
}

// 打印开户凭证
const printVoucher = () => {
  ElMessageBox.alert(`
    <div style="text-align: center; padding: 20px;">
      <h2>证券账户开户凭证</h2>
      <p><strong>账户类型：</strong>${accountType.value === 'PERSONAL' ? '个人账户' : '法人账户'}</p>
      <p><strong>账户号码：</strong>${newAccountNo.value}</p>
      <p><strong>开户时间：</strong>${new Date().toLocaleString()}</p>
      ${accountType.value === 'PERSONAL' ? `<p><strong>客户姓名：</strong>${formData.value.clientName}</p>` : `<p><strong>企业名称：</strong>${formData.value.corporateName}</p>`}
      <p style="margin-top: 20px;"><strong>请妥善保管此凭证</strong></p>
    </div>
  `, '开户凭证', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '确定',
    customClass: 'voucher-dialog'
  })
}

// 完成流程
const finishProcess = () => {
  activeStep.value = 0
  accountType.value = 'PERSONAL'
  resetForm()
}

// 重置表单
const resetForm = () => {
  formData.value = {
    clientName: '',
    gender: '',
    idCardNo: '',
    address: '',
    phone: '',
    profession: '',
    education: '',
    company: '',
    isAgent: '本人办理',
    proxyName: '',
    proxyIdCardNo: '',
    corporateName: '',
    businessLicenseNo: '',
    registrationNo: '',
    legalPersonName: '',
    legalPersonIdNo: '',
    legalPhone: '',
    legalAddress: '',
    agentName: '',
    agentIdNo: '',
    agentPhone: '',
    agentAddress: ''
  }
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
  
  // 重置密码相关
  passwordForm.value = { tradePassword: '', withdrawPassword: '' }
  hasSetPasswords.value = false
  showPasswordDialog.value = false
  
  // 重置合规检查相关
  complianceCheckResult.value = null
  compliancePassed.value = false
  
  // 重置步骤和账户号
  activeStep.value = 0
  newAccountNo.value = ''
}
</script>

<style scoped>
:deep(.el-form-item__error) {
  position: relative;
}

.el-form-item {
  margin-bottom: 28px;
}
</style>
