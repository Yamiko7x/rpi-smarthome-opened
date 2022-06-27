<template>
  <div
    class="actionsTableWrapper"
    :class="[showView ? 'showView' : 'hideView']"
  >
    <table v-if="display">
      <tr class="header">
        <th>Nazwa akcji</th>
        <th>Action ID</th>
        <th></th>
      </tr>
      <tr v-for="action in actionsDict" :key="action.action_id">
        <td @click="fnEditAction(action.action_id)">{{ action.name }}</td>
        <td @click="fnEditAction(action.action_id)">
          <FA-Icon
            v-if="this.workingActions.includes(action.action_id)"
            icon="cog"
            class="fa-spin"
            style="font-size: 0.8em; margin-right: 10px"
          />
          {{ action.action_id }}
        </td>
        <th>
          <FA-Icon
            icon="trash"
            class="trash"
            @click="rmAction(action.action_id)"
          />
        </th>
      </tr>
    </table>
    <div class="buttonsBar">
      <button @click="fnEditAction(-1)">Dodaj akcję</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "ActionsTable",
  props: {
    fnEditAction: {},
  },
  data() {
    return {
      showView: false,
      display: true,
      actionsDict: null,
      workingActions: [],
    };
  },
  watch: {},
  methods: {
    async rmAction(action_id) {
      if (this.workingActions.includes(action_id)) {
        this.$store.dispatch("addMsg", {
          type: "danger",
          msg: "Akcja może być usunięta wtedy gdy nie jest włączona.",
        });
      } else {
        if (confirm('Czy na pewno chcesz usunąć akcję: "'+action_id+'"?')) {
        } else {
          return false
        }
        await axios
          .post(
            "actions_api/rmAction",
            this.$store.getters.authDict({ action_id: action_id })
          )
          .then((result) => {
            if (result.data.auth && result.data.type == "success") {
              this.$store.dispatch("addMsg", {
                type: "info",
                msg: "Akcja " + action_id + " została usunięta.",
              });
              this.loadAllActions()
            } else this.$store.dispatch("handleLogout");
          })
          .catch((err) => {
            console.log(err);
            this.$store.dispatch("addMsg", {
              type: "danger",
              msg: "Cholibka, coś poszło nie tak :c",
            });
          });
      }
    },
    async loadAllActions() {
      await axios
        .post("actions_api/getAllActionsShorts", this.$store.getters.authDict())
        .then((result) => {
          console.log(result.data);
          if (result.data.auth) {
            this.actionsDict = result.data.actions_dict;
            this.workingActions = result.data.working_actions_ids;
          } else this.$store.dispatch("handleLogout");
        })
        .catch((err) => console.log(err));
    },
  },
  created() {
    setTimeout(() => {
      this.showView = true;
    }, this.$store.state.animationSpeed);
    this.loadAllActions();
  },
  components: {},
};
</script>

<style lang="scss" scoped>
.actionsTableWrapper {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin: auto;
  max-width: 600px;

  table {
    border-collapse: collapse;
    width: 100%;
    background-color: #fff;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);
    overflow-x: auto;

    td,
    th {
      text-align: left;
      padding: 8px;
      padding-left: 15px;
      font-size: 1.2em;
    }
    .actionBtn {
      text-align: center;
      padding: 5px 15px;
      margin: 0;
    }
    tr:not(.header):hover {
      background-color: rgb(179, 224, 255);
      cursor: pointer;
    }

    tr:nth-child(even) {
      background-color: #ebebeb;
    }

    .header {
      color: #fff;
      padding: 5px;
      background-color: rgb(27, 77, 110);
    }

    .trash {
      transition: 0.1s;
    }
    .trash:hover {
      color: rgb(253, 99, 94);
    }
  }

  .buttonsBar {
    width: 100%;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);

    button {
      font-size: 1.1em;
      width: 100%;
      border-left: 1px solid #fff;
      border-right: 1px solid #fff;
    }
  }
}
@media only screen and (max-width: 600px) {
}
</style>