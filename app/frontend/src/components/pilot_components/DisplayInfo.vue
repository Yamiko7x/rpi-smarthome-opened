<template>
  <div class="displayInfoWrapper">
    <div class="idle">
      <FA-Icon v-if="this.edit" icon="trash-can" class="faicon trash" pull="left" v-on:click="removeFn(this.id, this.name)"/>
      {{this.prefix}}{{this.state}}{{this.sufix}}
      <FA-Icon v-if="this.edit" icon="pen-to-square" class="faicon edit" pull="right" v-on:click="editComponent(this.allMeta)"/>
    </div>
  </div>
</template>

<script>
export default {
  name: "DisplayInfo",
  props: {
    id: { required: true },
    type: { required: true },
    state: { required: true },
    name: { required: false, defauld: '' },
    prefix: { required: false, defauld: '' },
    sufix: { required: false, defauld: '' },
    edit: { required: true },
    removeFn: { required: true },
    allMeta: { required: true },
    editComponent: { required: true },
  },
  data() {
    return {
    };
  },
  methods: {
  },
};
</script>

<style lang="scss" scoped>
.displayInfoWrapper{
  min-width: 100%;

  div{
    width: calc(100% - 30px);
    padding: 30px 10px;
    margin: 5px 0 0 0;
    border-radius: 10px;
    background-color: rgb(255, 255, 255);
  }
}
</style>