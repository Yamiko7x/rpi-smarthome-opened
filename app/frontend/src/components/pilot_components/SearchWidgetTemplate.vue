<template>
  <div
    class="searchWidgetTemplateWrapper"
    :class="[showView ? 'showView' : 'hideView']"
  >
    <div class="searchPanel">
      <div class="header">
        <div></div>
        <input type="text" placeholder="Szukaj szablonu" />
        <FA-Icon class="exit" icon="xmark" v-on:click="closeEvent('searchWidget')" />
      </div>

      <div
        v-for="(temp, idx) in templates"
        :key="idx"
        class="widgetTemplate"
        v-on:click="addComponent(temp)"
      >
        <p>{{ temp.name }}</p>
        <p>{{ temp.desc }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SearchWidgetTemplate",
  props: { closeEvent: { required: true }, addComponent: { required: true } },
  data() {
    return {
      showView: false,
      templates: [
        {
          type: "two_state_switch",
          name: "Przełącznik dwustanowy",
          desc: "Wybierz dwie akcje i przypisze je do włączenia oraz wyłączenia."
        },
        {
          type: "display_info",
          name: "Monitor informacyjny",
          desc: "Wskaż co ma monitorować i wyświetlaj informację.",
        },
      ],
    };
  },
  methods: {},
  created() {
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
  },
  components: {},
};
</script>

<style lang="scss" scoped>
.searchWidgetTemplateWrapper {
  position: fixed;
  top: 0;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  z-index: 80;

  .searchPanel {
    width: 90%;
    max-width: 600px;
    height: 90vh;
    margin: 5vh auto;
    background-color: #fff;
    box-shadow: 1px 1px 8px rgba(0, 0, 0, 0.3);

    .header {
      display: flex;
      flex-direction: row;
      justify-items: center;
      align-items: center;

      input {
        width: 70%;
        margin: 25px auto;
        box-shadow: none;
        border: 2px solid rgba(0, 0, 0, 0.2);
        border-radius: 10px;
      }
      input:focus {
        border: 2px solid rgba(94, 190, 253, 1);
      }
      .exit,
      div {
        width: 50px;
        font-size: 1.5em;
        transition: 0.2s;
      }
      .exit:hover {
        color: rgb(224, 93, 93);
        cursor: pointer;
      }
    }

    .widgetTemplate {
      display: flex;
      flex-direction: row;
      margin: 10px 20px;
      box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
      border: 2px solid rgb(94, 190, 253, 0);
      transition: 0.2s;

      p {
        padding: 10px 20px;
        border-right: 2px solid rgba(0, 0, 0, 0.4);
        text-align: left;
        width: 25%;
      }
      p:last-child {
        border: none;
        width: 75%;
      }
    }

    input {
      box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
      text-align: center;
    }
  }
  
  @media only screen and (max-width: 600px) {
    .searchPanel {
      width: 100%;
      height: 100%;
      margin: 0;
    }
  }

  .widgetTemplate:hover {
    border: 2px solid rgba(94, 190, 253, 1);
    cursor: pointer;
  }
}
</style>