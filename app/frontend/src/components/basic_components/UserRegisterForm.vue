<template>
  <div class="userregisterform-wrapper">
    
    <form class="registerForm" @submit.prevent="addUser()">
      <div>
        <label for="r_uname">Dane użytkownika</label>
        <input type="text" v-model="r_uname" placeholder="Nickname" />
        <input type="text" v-model="r_fname" placeholder="Imię" />
        <input type="text" v-model="r_lname" placeholder="Nazwisko" />
        <input type="email" v-model="r_email" placeholder="e-mail" />
        <input
          type="password"
          v-model="r_passwd1"
          :class="[this.lBorder]"
          placeholder="Hasło"
        />
        <input
          type="password"
          v-model="r_passwd2"
          :class="[this.lBorder]"
          placeholder="Hasło"
        />
      </div>
      <div>
        <label for="r_acctype">Typ konta</label>
        <select id="r_acctype" v-model="r_acctype">
          <option value="user">Użytkownik</option>
          <option value="admin">Administrator</option>
        </select>
        <input type="submit" value="Dodaj" />
      </div>
    </form>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "UserRegisterForm",
  props: {
    closeEvent: {required: true},
  },
  data() {
    return {
      r_acctype: "user",
      r_uname: "anon",
      r_fname: "Anonek",
      r_lname: "Anonowicz",
      r_email: "anon@wp.pl",
      r_passwd1: "Dr.Kokosik",
      r_passwd2: "Dr.Kokosik",
      r_passwd_ok: false,
      lBorder: "borderLeftBlue",
    };
  },
  methods: {
    async addUser() {
      if (this.checkCorrect(true)) {
        await axios
          .post("dbm_api/adduser", this.$store.getters.authDict({
            r_acctype: this.r_acctype,
            r_uname: this.r_uname,
            r_fname: this.r_fname,
            r_lname: this.r_lname,
            r_email: this.r_email,
            r_password: this.r_passwd1,
          }))
          .then((result) => {
            console.log(result.data);
            if (result.data.auth) {
              this.$store.dispatch("addMsg", { type: "info", msg: result.data.msg, });
              this.closeEvent(this.r_uname)
            } else {
              this.$store.dispatch("addMsg", { type: "danger", msg: result.data.msg, });
              this.$store.dispatch("handleLogout");
            }
          })
          .catch((err) => { console.log(err); });
      }
    },
    checkCorrect(lastCheck = false) {
      if (this.r_passwd1 != this.r_passwd2) {
        this.lBorder = "borderLeftRed";
        if (lastCheck)
          this.$store.dispatch("addMsg", {
            type: "danger",
            msg: "Oba pola muszą zawierać jednakowe hasła.",
          });
      } else if (this.r_passwd1 == this.r_passwd2) {
        if (this.$store.state.passwdRules.test(this.r_passwd1)) {
          this.lBorder = "borderLeftGreen";
          return true;
        } else if (lastCheck)
          this.$store.dispatch("addMsg", {
            type: "danger",
            msg: "Hasło musi zawierać co najmniej 1 cyfrę, wielką literę, małą literę i mieć co najmniej 6 znaków.",
          });
      }
      return false;
    },
  },
  watch: {
    r_passwd1() {
      this.checkCorrect();
    },
    r_passwd2() {
      this.checkCorrect();
    },
  },
  created() {
    this.checkCorrect();
  },
};
</script>

<style lang="scss" scoped>
.userregisterform-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: 15px;
}

.greenBorder {
  border-left: solid 4px rgb(92, 192, 92);
}
.redBorder {
  border-left: solid 4px rgb(204, 79, 57);
}
</style>