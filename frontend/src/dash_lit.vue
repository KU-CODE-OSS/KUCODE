<template>
  <v-app id="inspire">
    <v-app-bar flat>
      <v-container class="mx-auto d-flex align-center justify-center">
        <v-avatar class="me-4" color="grey-darken-1" size="32"></v-avatar>

        <v-btn
          v-for="link in links"
          :key="link"
          :text="link"
          variant="text"
        ></v-btn>

        <v-spacer></v-spacer>

        <v-responsive max-width="160">
          <v-text-field
            density="compact"
            label="Search"
            rounded="lg"
            variant="solo-filled"
            flat
            hide-details
            single-line
          ></v-text-field>
        </v-responsive>
      </v-container>
    </v-app-bar>

    <v-main class="bg-grey-lighten-3">
      <v-container>
        <v-row>
          <v-col cols="2">
            <v-sheet rounded="lg">
              <v-list rounded="lg">
                <div class="d-flex flex-row">
                  <v-tabs v-model="tab" color="primary" direction="vertical">
                    <v-tab
                      prepend-icon="mdi-account"
                      text="Option 1"
                      value="option-1"
                    ></v-tab>
                    <v-tab
                      prepend-icon="mdi-lock"
                      text="Option 2"
                      value="option-2"
                    ></v-tab>
                    <v-tab
                      prepend-icon="mdi-access-point"
                      text="Option 3"
                      value="option-3"
                    ></v-tab>
                    <v-tab
                      prepend-icon="mdi-access-point"
                      text="Option 4"
                      value="option-4"
                    ></v-tab>
                    <v-tab
                      prepend-icon="mdi-access-point"
                      text="Option 5"
                      value="option-5"
                    ></v-tab>
                  </v-tabs>
                </div>

                <v-divider class="my-2"></v-divider>

                <v-list-item
                  color="grey-lighten-4"
                  title="Refresh"
                  link
                ></v-list-item>
              </v-list>
            </v-sheet>
          </v-col>

          <v-col>
            <v-sheet min-height="70vh" rounded="lg">
              <v-tabs-window v-model="tab">
                <v-tabs-window-item value="option-1">
                  <v-card flat>
                    <v-card-text>
                      <p>
                        Sed aliquam ultrices mauris. Donec posuere vulputate
                        arcu. Morbi ac felis. Etiam feugiat lorem non metus. Sed
                        a libero.
                      </p>

                      <p>
                        Nam ipsum risus, rutrum vitae, vestibulum eu, molestie
                        vel, lacus. Aenean tellus metus, bibendum sed, posuere
                        ac, mattis non, nunc. Aliquam lobortis. Aliquam
                        lobortis. Suspendisse non nisl sit amet velit hendrerit
                        rutrum.
                      </p>

                      <p class="mb-0">
                        Phasellus dolor. Fusce neque. Fusce fermentum odio nec
                        arcu. Pellentesque libero tortor, tincidunt et,
                        tincidunt eget, semper nec, quam. Phasellus blandit leo
                        ut odio.
                      </p>
                    </v-card-text>
                  </v-card>
                </v-tabs-window-item>

                <v-tabs-window-item value="option-2">
                  <v-card flat>
                    <v-card-text>
                      <p>
                        Morbi nec metus. Suspendisse faucibus, nunc et
                        pellentesque egestas, lacus ante convallis tellus, vitae
                        iaculis lacus elit id tortor. Sed mollis, eros et
                        ultrices tempus, mauris ipsum aliquam libero, non
                        adipiscing dolor urna a orci. Curabitur ligula sapien,
                        tincidunt non, euismod vitae, posuere imperdiet, leo.
                        Nunc sed turpis.
                      </p>

                      <p>
                        Suspendisse feugiat. Suspendisse faucibus, nunc et
                        pellentesque egestas, lacus ante convallis tellus, vitae
                        iaculis lacus elit id tortor. Proin viverra, ligula sit
                        amet ultrices semper, ligula arcu tristique sapien, a
                        accumsan nisi mauris ac eros. In hac habitasse platea
                        dictumst. Fusce ac felis sit amet ligula pharetra
                        condimentum.
                      </p>

                      <p>
                        Sed consequat, leo eget bibendum sodales, augue velit
                        cursus nunc, quis gravida magna mi a libero. Nam commodo
                        suscipit quam. In consectetuer turpis ut velit. Sed
                        cursus turpis vitae tortor. Aliquam eu nunc.
                      </p>

                      <p>
                        Etiam ut purus mattis mauris sodales aliquam. Ut varius
                        tincidunt libero. Aenean viverra rhoncus pede. Duis leo.
                        Fusce fermentum odio nec arcu.
                      </p>

                      <p class="mb-0">
                        Donec venenatis vulputate lorem. Aenean viverra rhoncus
                        pede. In dui magna, posuere eget, vestibulum et, tempor
                        auctor, justo. Fusce commodo aliquam arcu. Suspendisse
                        enim turpis, dictum sed, iaculis a, condimentum nec,
                        nisi.
                      </p>
                    </v-card-text>
                  </v-card>
                </v-tabs-window-item>

                <v-tabs-window-item value="option-3">
                  <v-card flat>
                    <v-card-text>
                      <p>
                        Fusce a quam. Phasellus nec sem in justo pellentesque
                        facilisis. Nam eget dui. Proin viverra, ligula sit amet
                        ultrices semper, ligula arcu tristique sapien, a
                        accumsan nisi mauris ac eros. In dui magna, posuere
                        eget, vestibulum et, tempor auctor, justo.
                      </p>

                      <p class="mb-0">
                        Cras sagittis. Phasellus nec sem in justo pellentesque
                        facilisis. Proin sapien ipsum, porta a, auctor quis,
                        euismod ut, mi. Donec quam felis, ultricies nec,
                        pellentesque eu, pretium quis, sem. Nam at tortor in
                        tellus interdum sagittis.
                      </p>
                    </v-card-text>
                  </v-card>
                </v-tabs-window-item>

                <v-tabs-window-item value="option-4">
                  <v-card flat>
                    <v-card-text>
                      <p>
                        Fusce a quam. Phasellus nec sem in justo pellentesque
                        facilisis. Nam eget dui. Proin viverra, ligula sit amet
                        ultrices semper, ligula arcu tristique sapien, a
                        accumsan nisi mauris ac eros. In dui magna, posuere
                        eget, vestibulum et, tempor auctor, justo.
                      </p>

                      <p class="mb-0">
                        Cras sagittis. Phasellus nec sem in justo pellentesque
                        facilisis. Proin sapien ipsum, porta a, auctor quis,
                        euismod ut, mi. Donec quam felis, ultricies nec,
                        pellentesque eu, pretium quis, sem. Nam at tortor in
                        tellus interdum sagittis.
                      </p>
                    </v-card-text>
                  </v-card>
                </v-tabs-window-item>

                <v-tabs-window-item value="option-5">
                  <v-card flat>
                    <v-card-text>
                      <p>
                        Fusce a quam. Phasellus nec sem in justo pellentesque
                        facilisis. Nam eget dui. Proin viverra, ligula sit amet
                        ultrices semper, ligula arcu tristique sapien, a
                        accumsan nisi mauris ac eros. In dui magna, posuere
                        eget, vestibulum et, tempor auctor, justo.
                      </p>

                      <p class="mb-0">
                        Cras sagittis. Phasellus nec sem in justo pellentesque
                        facilisis. Proin sapien ipsum, porta a, auctor quis,
                        euismod ut, mi. Donec quam felis, ultricies nec,
                        pellentesque eu, pretium quis, sem. Nam at tortor in
                        tellus interdum sagittis.
                      </p>
                    </v-card-text>
                  </v-card>
                </v-tabs-window-item>
              </v-tabs-window>
              <!-- 여기 테이블 컴포넌트로 불러오면 좋을 듯  -->
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
  const links = ['정보관리', '통계분석', '커뮤니티', '공지사항']
</script>

<script>
  export default {
    name: 'DashboardComponent',
    data: () => ({
      tab: 'option-1',
      links: ['정보관리', '통계분석', '커뮤니티', '공지사항'],
    }),
  }
</script>
