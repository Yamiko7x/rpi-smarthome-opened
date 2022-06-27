<template>
  <div class="popupBoxWrapper">
    <div class="popupBoxInfo">
      <div class="closeIcon">
        <FA-Icon icon="close" class="icon" @click="this.closeEvent()" />
      </div>
      <p v-for="m in messages" :key="m">
        {{m}}<br>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "PopupBox",
  props: {
    closeEvent: { required: true },
    messages: {required: false, default: ['Some text here']}
  },
  data() {
    return {
    };
  },
  methods: {
  },
  watch: {
  },
  created() {
  },
};
</script>

<style lang="scss" scoped>

.popupBoxWrapper {
  position: fixed;
  z-index: 50;
  padding: 0;
  margin: 0;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.3);

  .popupBoxInfo {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    width: 50%;
    min-height: 200px;
    max-width: 600px;
    background-color: #fff;
    padding: 20px;
    padding-top: 5px;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.3);
    border: solid 2px rgb(84, 149, 192);

    .closeIcon {
      width: 100%;
      text-align: right;
      margin: 0;
      padding: 0;
    }
    .closeIcon .icon:hover{
      color: rgb(253, 99, 94);
      cursor: pointer;
    }
  }
  
  @media only screen and (max-width: 600px) {
    .popupBox {
      width: 100%;
    }
  }
}
</style>