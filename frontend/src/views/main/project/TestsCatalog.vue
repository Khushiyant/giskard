<template>
  <div v-if='testFunctions.length > 0' class='vc mt-2 pb-0'>
    <div class='vc'>
      <v-container class='main-container vc'>
        <v-alert v-if='!hasGiskardTests' border='left' color='warning' colored-border icon='warning' outlined>
          <span>Giskard test are not available.</span>
          <StartWorkerInstructions />
        </v-alert>
        <v-row class='fill-height'>
          <v-col class='vc fill-height' cols='4'>
            <v-text-field v-model='searchFilter' append-icon='search' label='Search test' outlined></v-text-field>
            <v-list class='vc fill-height' three-line>
              <v-list-item-group v-model='selected' color='primary' mandatory>
                <template v-for='test in filteredTestFunctions'>
                  <v-divider />
                  <v-list-item :value='test'>
                    <v-list-item-content>
                      <v-list-item-title class='test-title'>
                        <div class='d-flex align-center'>
                          <span class='list-test-name'>{{ test.displayName ?? test.name }}</span>
                          <v-spacer class='flex-grow-1' />
                          <v-tooltip v-if='test.potentiallyUnavailable' bottom>
                            <template v-slot:activator='{ on, attrs }'>
                              <div v-bind='attrs' v-on='on'>
                                <v-icon color='orange'>warning</v-icon>
                              </div>
                            </template>
                            <span>This test is potentially unavailable. Start your external ML worker to display available tests.</span>
                          </v-tooltip>
                        </div>
                      </v-list-item-title>
                      <v-list-item-subtitle v-if='test.tags'>
                        <v-chip v-for='tag in alphabeticallySorted(test.tags)' :color='pasterColor(tag)' class='mr-2'
                                x-small>
                          {{ tag }}
                        </v-chip>
                      </v-list-item-subtitle>
                    </v-list-item-content>

                  </v-list-item>
                </template>
              </v-list-item-group>
            </v-list>
          </v-col>

          <v-col v-if='selected' class='vc fill-height' cols='8'>
            <div class='d-flex justify-space-between py-2'>
              <span class='selected-test-name'>{{ selected.displayName ?? selected.name }}</span>
              <v-btn class='primaryLightBtn' color='primaryLight' @click='addToTestSuite'>
                <v-icon left>mdi-plus</v-icon>
                Add to test suite
              </v-btn>
            </div>

            <div class='vc overflow-x-hidden pr-5'>
              <v-alert v-if='selected.potentiallyUnavailable' border='left' color='warning' colored-border
                       icon='warning'
                       outlined>
                <span>This test is potentially unavailable. Start your external ML worker to display available tests.</span>
                <pre></pre>
                <StartWorkerInstructions />
              </v-alert>

              <div id='description-group' class='py-4'>
                <v-expansion-panels v-model='panel' flat multiple>
                  <v-expansion-panel>
                    <v-expansion-panel-header class='pl-0'>
                      <div class='d-flex align-center'>
                        <v-icon class='group-icon pb-1 mr-1' left>mdi-text-box</v-icon>
                        <span class='group-title'>Description</span>
                        <v-icon v-if='panel.includes(0)' right>mdi-chevron-up</v-icon>
                        <v-icon v-else right>mdi-chevron-down</v-icon>
                      </div>
                      <template v-slot:actions>
                        <span></span>
                      </template>
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <p class='selected-test-description pt-2 mb-4'>{{ doc.body }}</p>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </div>

              <div id='inputs-group' class='py-4 mb-4'>
                <div class='d-flex'>
                  <v-icon class='group-icon pb-1 mr-1' left>mdi-pencil-box</v-icon>
                  <span class='group-title'>Inputs</span>
                  <v-spacer></v-spacer>
                </div>
                <SuiteInputListSelector :doc='doc' :editing='true' :inputs='inputType'
                                        :modelValue='testArguments' :project-id='props.projectId' :test='selected' />
                <div class='d-flex'>
                  <v-spacer></v-spacer>
                  <v-menu offset-y>
                    <template v-slot:activator='{ on, attrs }'>
                      <v-btn class='primaryLightBtn' v-bind='attrs' color='primaryLight' small width='100'
                             :loading='testRunning' @click='() => runTest(true)'>
                        <v-icon>arrow_right</v-icon>
                        <span class='pe-2'>Run</span>
                        <v-icon class='ps-2 primary-left-border' v-on='on' @click.stop>mdi-menu-down</v-icon>
                      </v-btn>
                    </template>
                    <v-list>
                      <v-list-item>
                        <v-tooltip bottom>
                          <template v-slot:activator='{ on, attrs }'>
                            <v-btn color='secondary' text v-bind='attrs'
                                   @click='() => runTest(false)'
                                   v-on='on' :loading='testRunning'>
                              <v-icon>science</v-icon>
                              Run on whole dataset
                            </v-btn>
                          </template>
                          <span>By default we try the test on a sample to fasten execution.</span>
                        </v-tooltip>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </div>
                <TestExecutionResultBadge v-if='testResult' :result='testResult' class='mt-4' />
              </div>

              <div id='usage-group' class='py-4 mb-4'>
                <div class='d-flex'>
                  <v-icon class='group-icon pb-1 mr-1' left>mdi-code-greater-than</v-icon>
                  <span class='group-title'>How to use with code</span>
                </div>
                <CodeSnippet :key="selected.name + '_usage'" :codeContent='selectedTestUsage' :language="'python'"
                             class='mt-2'></CodeSnippet>
              </div>

              <div id='code-group' class='py-4'>
                <div class='d-flex'>
                  <v-icon class='group-icon pb-1 mr-1' left>mdi-code-braces-box</v-icon>
                  <span class='group-title'>Source code</span>
                </div>
                <CodeSnippet :key="selected.name + '_source_code'" :codeContent='selected.code'
                             class='mt-2'></CodeSnippet>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
  <v-container v-else class='d-flex flex-column vc fill-height'>
    <h1 class='pt-16'>ML Worker is not connected</h1>
    <StartWorkerInstructions />
  </v-container>
</template>

<script lang='ts' setup>
import { chain } from 'lodash';
import { api } from '@/api';
import { computed, onActivated, ref, watch } from 'vue';
import { anonymize, pasterColor } from '@/utils';
import TestExecutionResultBadge from '@/views/main/project/TestExecutionResultBadge.vue';
import { FunctionInputDTO, TestFunctionDTO, TestTemplateExecutionResultDTO } from '@/generated-sources';
import AddTestToSuite from '@/views/main/project/modals/AddTestToSuite.vue';
import { $vfm } from 'vue-final-modal';
import StartWorkerInstructions from '@/components/StartWorkerInstructions.vue';
import { storeToRefs } from 'pinia';
import { useCatalogStore } from '@/stores/catalog';
import SuiteInputListSelector from '@/components/SuiteInputListSelector.vue';
import { extractArgumentDocumentation } from '@/utils/python-doc.utils';
import { alphabeticallySorted } from '@/utils/comparators';
import CodeSnippet from '@/components/CodeSnippet.vue';
import mixpanel from 'mixpanel-browser';

const props = defineProps<{
  projectId: number,
  suiteId?: number
}>();


const searchFilter = ref<string>('');
const { testFunctions } = storeToRefs(useCatalogStore());
const selected = ref<TestFunctionDTO | null>(null);
const testArguments = ref<{ [name: string]: FunctionInputDTO }>({});
const testRunning = ref<boolean>(false);
const testResult = ref<TestTemplateExecutionResultDTO | null>(null);

const panel = ref<number[]>([0]);

const selectedTestUsage = computed(() => {

  if (selected.value === null) {
    return '';
  }

  let content = '';

  const requiredArgs = selected.value.args.filter(arg => !arg.optional && arg.name !== 'kwargs');
  const uniqueImports = [
    ...chain(requiredArgs)
      .map('type')
      .uniq()
      .value()
      .filter(i => i !== 'str'),
    selected.value.name
  ];

  content += `from giskard import ${uniqueImports.join(', ')}`;
  content += '\n\n';

  requiredArgs.forEach(arg => {
    content += `${arg.name} = ${arg.type}(...)`;
    content += '\n';
  });
  content += '\n';

  const parametersWithDefaults = selected.value.args.map(arg => {
    if (arg.name === 'kwargs') return '**kwargs';
    if (arg.optional) return `${arg.name}=${arg.defaultValue}`;
    return arg.name;
  });
  content += `test_result, passed = ${selected.value.name}(${parametersWithDefaults.join(', ')})`;
  content += '\n\n';

  content += `print(f"TEST RESULT: {test_result} - PASSED: {passed}")`;

  return content;
});


async function runTest(sample: boolean) {
  testResult.value = null;
  testRunning.value = true;

  try {
    mixpanel.track('Run test from Catalog', {
      testName: selected.value!.name,
      inputs: anonymize(Object.values(testArguments.value)),
      sample
    });

    testResult.value = await api.runAdHocTest(props.projectId, selected.value!.uuid, Object.values(testArguments.value), sample);
  } finally {
    testRunning.value = false;
  }
}


watch(selected, (value) => {
  testResult.value = null;

  if (value === null || value === undefined) {
    return;
  }

  testArguments.value = chain(value.args)
    .keyBy('name')
    .mapValues(arg => ({
      name: arg.name,
      isAlias: false,
      type: arg.type,
      value: arg.optional ? arg.defaultValue : null
    }))
    .value();
});

const doc = computed(() => extractArgumentDocumentation(selected.value));

const hasGiskardTests = computed(() => {
  return testFunctions.value.find(t => t.tags.includes('giskard')) !== undefined;
});

const filteredTestFunctions = computed(() => {
  return chain(testFunctions.value)
    .filter((func) => {
      const keywords = searchFilter.value.split(' ')
        .map(keyword => keyword.trim().toLowerCase())
        .filter(keyword => keyword !== '');

      return keywords.filter(keyword =>
        func.name.toLowerCase().includes(keyword)
        || func.doc?.toLowerCase()?.includes(keyword)
        || func.displayName?.toLowerCase()?.includes(keyword)
      ).length === keywords.length;
    })
    .sortBy(t => t.displayName ?? t.name)
    .value();
});

onActivated(async () => {
  if (testFunctions.value.length > 0) {
    selected.value = testFunctions.value[0];
  }
});

function addToTestSuite() {
  $vfm.show({
    component: AddTestToSuite,
    bind: {
      projectId: props.projectId,
      test: selected.value,
      suiteId: props.suiteId,
      testArguments: testArguments.value
    }
  });
}

const inputType = computed(() => chain(selected.value?.args ?? [])
  .keyBy('name')
  .mapValues('type')
  .value()
);

</script>

<style lang='scss' scoped>
.main-container {
  width: 100%;
  max-width: 100%;
}

.test-title {
  white-space: break-spaces;
}

.box-grow {
  flex: 1;
  /* formerly flex: 1 0 auto; */
  background: green;
  padding: 5px;
  margin: 5px;
  min-height: 0;
  /* new */
}

::v-deep .v-expansion-panel-content__wrap {
  padding: 0;
}

.selected-test-description {
  white-space: break-spaces;
}

.group-title {
  font-size: 1.25rem;
  font-weight: 500;
  letter-spacing: normal;
}

.group-icon {
  color: #087038;
  font-size: 1.25rem;
  margin-top: 0.3rem;
}

.selected-test-name {
  font-weight: 600;
  font-size: 1.75rem;
}

.list-test-name {
  font-weight: 500;
}

.primary-left-border {
  border-left: 1px solid #087038;
}
</style>
