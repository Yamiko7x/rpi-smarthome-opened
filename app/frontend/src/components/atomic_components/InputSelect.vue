<template>
  <select v-model="this.compoDict[this.rules.prop]" class="borderLeftGreen">
    <option v-for="opt in this.rules.options" :key="opt[0]" :value="opt[0]">{{opt[1]}}</option>
  </select>
</template>

<script>
export default {
  name: "InputSelect",
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
  },
  created() {
  },
};
</script>

<style lang="scss" scoped>
</style>