<template>
  <input type="number" v-model="this.compoDict[this.rules.prop]" :min="this.rules.min" :max="this.rules.max" class="borderLeftGreen" :placeholder="this.rules.placeholder">
</template>

<script>
export default {
  name: "InputNumber",
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