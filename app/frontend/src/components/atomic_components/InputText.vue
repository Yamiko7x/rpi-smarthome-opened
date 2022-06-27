<template>
  <input type="text" v-model="this.compoDict[this.rules.prop]" :placeholder="this.rules.placeholder" :class="[this.checkCorrect()]">
</template>

<script>
export default {
  name: "InputText",
  components: {
  },
  props: {
    compoDict: { required: true },
    rules: { required: true },
  },
  data() {
    return {
    };
  },
  watch: {},
  methods: {
    checkCorrect(){
      if(this.rules.required) {
        if(this.compoDict[this.rules.prop]){}else{
          if (Number.isInteger(this.compoDict[this.rules.prop])) {
            this.compoDict[this.rules.prop] = this.compoDict[this.rules.prop].toString()
            }else this.compoDict[this.rules.prop] = ''
        }
        if(this.compoDict[this.rules.prop].length > 0) return "borderLeftGreen"
        else return "borderLeftRed"
      } else return "borderLeftBlue"
    }
  },
  created() {
  },
};
</script>

<style lang="scss" scoped>
  input{
    width: 100%;
  }
</style>